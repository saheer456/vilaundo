import asyncio
import logging
import os
import datetime
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .scrapers import agmarknet, horticorp

scheduler = None

from sqlalchemy import text
from .db import AsyncSessionLocal

scheduler = None

async def sync_all_prices():
    """Fetch prices from scrapers, normalize and upsert into database.
    Relies on commodities and districts being present (seeded).
    """
    logging.info("Starting price sync...")
    try:
        ag_prices = await agmarknet.fetch_agmarknet_prices()
        hc_prices = await horticorp.fetch_horticorp_prices()
        records = []
        if ag_prices:
            records.extend(ag_prices)
        if hc_prices:
            records.extend(hc_prices)

        logging.info("Fetched %d total records", len(records))

        if not records:
            logging.info("No records found; nothing to upsert")
            return

        async with AsyncSessionLocal() as session:
            # Query commodities and districts using text()
            res_c = await session.execute(text("SELECT id, name_en FROM commodities"))
            commodities = {r['name_en'].lower().strip(): r['id'] for r in res_c.mappings().all()}

            res_d = await session.execute(text("SELECT id, name_en FROM districts"))
            districts = {r['name_en'].lower().strip(): r['id'] for r in res_d.mappings().all()}

            upserted = 0
            for r in records:
                commodity_name = r.get('commodity_name_en') or r.get('commodity') or r.get('name_en')
                district_name = r.get('district_name_en') or r.get('district') or r.get('district_en')
                price_min = r.get('price_min')
                price_max = r.get('price_max')
                price_modal = r.get('price_modal')
                
                if price_modal is None and price_min is not None and price_max is not None:
                    try:
                        price_modal = (float(price_min) + float(price_max)) / 2
                    except Exception:
                        price_modal = price_min or price_max
                
                # Normalize values
                if price_min is not None:
                    price_min = float(price_min)
                if price_max is not None:
                    price_max = float(price_max)
                if price_modal is not None:
                    price_modal = float(price_modal)
                
                date_val_raw = r.get('date') or datetime.date.today().isoformat()
                if isinstance(date_val_raw, str):
                    date_val = datetime.datetime.strptime(date_val_raw[:10], "%Y-%m-%d").date().isoformat()
                else:
                    date_val = date_val_raw.isoformat() if hasattr(date_val_raw, 'isoformat') else str(date_val_raw)
                
                source = r.get('source') or 'SCRAPER'

                if not commodity_name or not district_name:
                    continue

                comm_id = commodities.get(commodity_name.lower().strip())
                dist_id = districts.get(district_name.lower().strip())

                if not comm_id or not dist_id:
                    # Try partial match if exact match is not found
                    for name, cid in commodities.items():
                        if name in commodity_name.lower() or commodity_name.lower() in name:
                            comm_id = cid
                            break
                    for name, did in districts.items():
                        if name in district_name.lower() or district_name.lower() in name:
                            dist_id = did
                            break

                if not comm_id or not dist_id:
                    continue

                # Query if price already exists
                q = text("SELECT id FROM prices WHERE commodity_id = :comm_id AND district_id = :dist_id AND date = :date")
                res_p = await session.execute(q, {
                    "comm_id": comm_id,
                    "dist_id": dist_id,
                    "date": date_val
                })
                existing_row = res_p.first()

                if existing_row:
                    price_id = existing_row[0]
                    # Update
                    await session.execute(
                        text("UPDATE prices SET price_min = :pmin, price_max = :pmax, price_modal = :pmodal, source = :src WHERE id = :id"),
                        {
                            "pmin": price_min,
                            "pmax": price_max,
                            "pmodal": price_modal,
                            "src": source,
                            "id": price_id
                        }
                    )
                else:
                    # Insert
                    import uuid
                    price_id = str(uuid.uuid4())
                    await session.execute(
                        text("INSERT INTO prices (id, commodity_id, district_id, price_min, price_max, price_modal, date, source) "
                             "VALUES (:id, :comm_id, :dist_id, :pmin, :pmax, :pmodal, :date, :src)"),
                        {
                            "id": price_id,
                            "comm_id": comm_id,
                            "dist_id": dist_id,
                            "pmin": price_min,
                            "pmax": price_max,
                            "pmodal": price_modal,
                            "date": date_val,
                            "src": source
                        }
                    )
                upserted += 1

            await session.commit()
            logging.info('Price sync complete: %d records upserted/updated', upserted)

    except Exception as e:
        logging.exception('Price sync failed: %s', e)


def start_scheduler():
    """Start APScheduler to run sync_all_prices daily at 07:30 IST.
    The scheduler can be disabled by setting DISABLE_SCHEDULER=1 in the environment (useful for tests).
    """
    global scheduler
    if os.getenv('DISABLE_SCHEDULER') == '1':
        logging.info('Scheduler disabled via DISABLE_SCHEDULER env var')
        return
    if scheduler is not None:
        return
    scheduler = AsyncIOScheduler()
    # Schedule job: at 07:30 Asia/Kolkata daily
    scheduler.add_job(lambda: asyncio.create_task(sync_all_prices()), 'cron', hour=7, minute=30, timezone='Asia/Kolkata')
    scheduler.start()
    logging.info('APScheduler started')
