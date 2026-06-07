from fastapi import FastAPI
from datetime import date
from . import tasks

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
    """Return today's prices (stub)."""
    return {
        "date": date.today().isoformat(),
        "district": district or "All",
        "prices": []
    }

@app.post("/admin/sync")
async def admin_sync():
    """Trigger an immediate sync of prices."""
    await tasks.sync_all_prices()
    return {"status": "sync_started"}
