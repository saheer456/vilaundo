from fastapi import FastAPI, HTTPException
from datetime import date
import os
from . import tasks
from . import api as api_module

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Start scheduler (non-blocking)
    tasks.start_scheduler()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/prices/today")
async def prices_today(district: str = None):
    """Return today's prices. If DATABASE_URL is set, prefer DB (not yet implemented), otherwise run scrapers live."""
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if DATABASE_URL:
        # DB integration not implemented yet; inform client
        return {
            "date": date.today().isoformat(),
            "district": district or "All",
            "prices": [],
            "note": "DB mode enabled but read-from-db not implemented yet."
        }

    # Scrape live from sources
    prices = await api_module.fetch_live_prices(district=district)
    return {
        "date": date.today().isoformat(),
        "district": district or "All",
        "prices": prices
    }

@app.post("/admin/sync")
async def admin_sync():
    """Trigger an immediate sync of prices into DB (if configured)."""
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if not DATABASE_URL:
        raise HTTPException(status_code=400, detail="DATABASE_URL not set; cannot sync to DB")
    await tasks.sync_all_prices()
    return {"status": "sync_started"}
