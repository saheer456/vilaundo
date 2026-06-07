import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .scrapers import agmarknet, horticorp

scheduler = None

async def sync_all_prices():
    logging.info("Starting price sync...")
    try:
        ag_prices = await agmarknet.fetch_agmarknet_prices()
        hc_prices = await horticorp.fetch_horticorp_prices()
        logging.info("Fetched %d agmarknet records, %d horticorp records", len(ag_prices), len(hc_prices))
        # TODO: normalize records and insert/update into DB (Supabase/Postgres)
    except Exception as e:
        logging.exception("Price sync failed: %s", e)


def start_scheduler():
    """Start APScheduler to run sync_all_prices daily at 07:30 IST."""
    global scheduler
    if scheduler is not None:
        return
    scheduler = AsyncIOScheduler()
    # Schedule job: at 07:30 Asia/Kolkata daily
    scheduler.add_job(lambda: asyncio.create_task(sync_all_prices()), 'cron', hour=7, minute=30, timezone='Asia/Kolkata')
    scheduler.start()
    logging.info("APScheduler started")
