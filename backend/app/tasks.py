import asyncio
import logging
import os
import datetime
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .scrapers import agmarknet, horticorp

scheduler = None

async def sync_all_prices():
    """Fetch prices from scrapers, normalize and upsert into Postgres (prices table).
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

        DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
        if not DATABASE_URL:
            logging.error('DATABASE_URL or SUPABASE_DB_URL not set; cannot write to DB')
            return

        conn = await asyncpg.connect(DATABASE_URL)
        try:
            upserted = 0
            for r in records:
                commodity = r.get('commodity_name_en') or r.get('commodity') or r.get('name_en')
                district = r.get('district_name_en') or r.get('district') or r.get('district_en')
                price_min = r.get('price_min')
                price_max = r.get('price_max')
                price_modal = r.get('price_modal')
                if price_modal is None and price_min is not None and price_max is not None:
                    try:
                        price_modal = (float(price_min) + float(price_max)) / 2
                    except Exception:
                        price_modal = price_min or price_max
                date_val = r.get('date') or datetime.date.today().isoformat()
                source = r.get('source') or r.get('source_name') or 'SCRAPER'

                if not commodity or not district:
                    logging.warning('Skipping record with missing commodity/district: %s', r)
                    continue

                # lookup ids
                commodity_row = await conn.fetchrow('SELECT id FROM commodities WHERE name_en = $1', commodity)
                if not commodity_row:
                    logging.warning('Unknown commodity (not seeded): %s', commodity)
                    continue
                commodity_id = commodity_row['id']

                district_row = await conn.fetchrow('SELECT id FROM districts WHERE name_en = $1', district)
                if not district_row:
                    logging.warning('Unknown district (not seeded): %s', district)
                    continue
                district_id = district_row['id']

                # Upsert into prices
                await conn.execute('''
                    INSERT INTO prices (commodity_id, district_id, price_min, price_max, price_modal, date, source)
                    VALUES ($1,$2,$3,$4,$5,$6,$7)
                    ON CONFLICT (commodity_id, district_id, date) DO UPDATE
                    SET price_min = EXCLUDED.price_min,
                        price_max = EXCLUDED.price_max,
                        price_modal = EXCLUDED.price_modal,
                        source = EXCLUDED.source,
                        created_at = NOW();
                ''', commodity_id, district_id, price_min, price_max, price_modal, date_val, source)
                upserted += 1

            logging.info('Upsert complete: %d records', upserted)
        finally:
            await conn.close()

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
