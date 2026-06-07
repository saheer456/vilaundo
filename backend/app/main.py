from fastapi import FastAPI, HTTPException, Depends
from datetime import date, timedelta
import os
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import tasks
from . import api as api_module
from .db import get_session

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Start scheduler (non-blocking)
    tasks.start_scheduler()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/commodities")
async def list_commodities(session: AsyncSession = Depends(get_session)):
    q = text("SELECT id, name_en, name_ml, category, unit FROM commodities ORDER BY name_en")
    res = await session.execute(q)
    rows = [dict(r) for r in res.mappings().all()]
    return {"commodities": rows}

@app.get("/api/districts")
async def list_districts(session: AsyncSession = Depends(get_session)):
    q = text("SELECT id, name_en, name_ml, region FROM districts ORDER BY name_en")
    res = await session.execute(q)
    rows = [dict(r) for r in res.mappings().all()]
    return {"districts": rows}

@app.get("/api/prices/today")
async def prices_today(district: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    """Return today's prices. Reads from DB if available; otherwise scrapes live."""
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    today = date.today().isoformat()
    if not DATABASE_URL:
        prices = await api_module.fetch_live_prices(district=district)
        return {"date": today, "district": district or "All", "prices": prices}

    # query DB for today's prices
    q = text(
        "SELECT p.date, c.id as commodity_id, c.name_en, c.name_ml, c.category, c.unit, d.name_en as district, p.price_min, p.price_max, p.price_modal, p.source"
        " FROM prices p"
        " LEFT JOIN commodities c ON p.commodity_id = c.id"
        " LEFT JOIN districts d ON p.district_id = d.id"
        " WHERE p.date = :date"
        " "
    )
    params = {"date": today}
    if district:
        q = text(q.text + " AND d.name_en = :district")
        params["district"] = district
    q = text(q.text + " ORDER BY c.name_en")
    res = await session.execute(q, params)
    rows = [
        {
            "commodity_id": r["commodity_id"],
            "name_en": r["name_en"],
            "name_ml": r["name_ml"],
            "category": r["category"],
            "unit": r["unit"],
            "district": r["district"],
            "price_min": r["price_min"],
            "price_max": r["price_max"],
            "price_modal": r["price_modal"],
            "source": r["source"],
            "date": r["date"].isoformat() if hasattr(r["date"], 'isoformat') else r["date"]
        }
        for r in res.mappings().all()
    ]
    return {"date": today, "district": district or "All", "prices": rows}

@app.get("/api/prices/{commodity_id}/history")
async def commodity_history(commodity_id: str, district: Optional[str] = None, days: int = 30, session: AsyncSession = Depends(get_session)):
    end = date.today()
    start = (end - timedelta(days=days)).isoformat()
    params = {"commodity_id": commodity_id, "start": start}
    qtext = "SELECT date, price_modal FROM prices WHERE commodity_id = :commodity_id AND date >= :start"
    if district:
        # resolve district id
        dres = await session.execute(text("SELECT id FROM districts WHERE name_en = :name"), {"name": district})
        drow = dres.first()
        if not drow:
            return {"history": []}
        params["district_id"] = drow[0]
        qtext += " AND district_id = :district_id"
    qtext += " ORDER BY date ASC"
    res = await session.execute(text(qtext), params)
    rows = [{"date": r["date"].isoformat() if hasattr(r["date"], 'isoformat') else r["date"], "price_modal": r["price_modal"]} for r in res.mappings().all()]
    return {"commodity_id": commodity_id, "history": rows}

@app.get("/api/prices/trending")
async def trending(session: AsyncSession = Depends(get_session)):
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    q = text(
        "SELECT c.id as commodity_id, c.name_en, p_today.price_modal as today_price, p_y.price_modal as yesterday_price, (p_today.price_modal - p_y.price_modal) as change"
        " FROM prices p_today"
        " JOIN commodities c ON p_today.commodity_id = c.id"
        " LEFT JOIN prices p_y ON p_y.commodity_id = p_today.commodity_id AND p_y.date = :yesterday"
        " WHERE p_today.date = :today"
        " ORDER BY ABS(change) DESC LIMIT 20"
    )
    res = await session.execute(q, {"today": today, "yesterday": yesterday})
    rows = []
    for r in res.mappings().all():
        today_price = r.get('today_price')
        yesterday_price = r.get('yesterday_price')
        change = r.get('change')
        change_percent = None
        if yesterday_price:
            try:
                change_percent = (change / yesterday_price) * 100
            except Exception:
                change_percent = None
        trend = 'up' if change and change > 0 else ('down' if change and change < 0 else 'flat')
        rows.append({
            'commodity_id': r.get('commodity_id'),
            'name_en': r.get('name_en'),
            'today_price': today_price,
            'yesterday_price': yesterday_price,
            'change': change,
            'change_percent': change_percent,
            'trend': trend
        })
    return {'date': today, 'trending': rows}

@app.post("/admin/sync")
async def admin_sync():
    """Trigger an immediate sync of prices into DB (if configured)."""
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if not DATABASE_URL:
        raise HTTPException(status_code=400, detail="DATABASE_URL not set; cannot sync to DB")
    await tasks.sync_all_prices()
    return {"status": "sync_started"}
