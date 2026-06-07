from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
import os
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import tasks
from . import api as api_module
from .db import get_session

app = FastAPI()

# Allow CORS from local frontend preview/dev servers so the static preview can call the API
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

from pydantic import BaseModel
import uuid

class CommunitySubmit(BaseModel):
    commodity_id: str
    district_id: str
    price: float
    market_name: Optional[str] = None

class AlertCreate(BaseModel):
    commodity_id: str
    district_id: str
    threshold_price: float
    direction: str # 'above' or 'below'

@app.get("/api/prices/today")
async def prices_today(district: Optional[str] = None, session: AsyncSession = Depends(get_session)):
    """Return today's prices. Reads from DB if available; otherwise scrapes live."""
    today = date.today()
    today_str = today.isoformat()
    
    # Check if there are any prices for today
    res_count = await session.execute(
        text("SELECT COUNT(*) FROM prices WHERE date = :date"),
        {"date": today_str}
    )
    count = res_count.scalar()
    
    delayed = False
    target_date = today_str
    
    if count == 0:
        # DB doesn't have prices for today. Let's try running sync_all_prices to fetch live
        try:
            await tasks.sync_all_prices()
            res_count2 = await session.execute(
                text("SELECT COUNT(*) FROM prices WHERE date = :date"),
                {"date": today_str}
            )
            count = res_count2.scalar()
        except Exception as e:
            logging.error("Failed to run automatic sync: %s", e)
            
        if count == 0:
            # Sync did not populate today's data (e.g. offline). Fetch last available date.
            res_max = await session.execute(text("SELECT MAX(date) FROM prices"))
            max_date = res_max.scalar()
            if max_date:
                target_date = max_date.isoformat() if hasattr(max_date, 'isoformat') else str(max_date)
                delayed = True
            else:
                # Fallback to fetching live prices directly without DB
                prices = await api_module.fetch_live_prices(district=district)
                return {"date": today_str, "district": district or "All", "prices": prices, "delayed": True}

    # Fetch target_date prices
    q = text(
        "SELECT p.date, c.id as commodity_id, c.name_en, c.name_ml, c.category, c.unit, d.name_en as district, p.price_min, p.price_max, p.price_modal, p.source"
        " FROM prices p"
        " LEFT JOIN commodities c ON p.commodity_id = c.id"
        " LEFT JOIN districts d ON p.district_id = d.id"
        " WHERE p.date = :date"
    )
    params = {"date": target_date}
    if district:
        q = text(q.text + " AND d.name_en = :district")
        params["district"] = district
    q = text(q.text + " ORDER BY c.name_en")
    
    res = await session.execute(q, params)
    today_rows = [dict(r) for r in res.mappings().all()]
    
    # Calculate yesterday's prices to compute changes and trends
    try:
        target_dt = datetime.date.fromisoformat(target_date) if isinstance(target_date, str) else target_date
    except Exception:
        target_dt = today
    yesterday_str = (target_dt - timedelta(days=1)).isoformat()
    
    q_prev = text(
        "SELECT p.commodity_id, d.name_en as district, p.price_modal"
        " FROM prices p"
        " LEFT JOIN districts d ON p.district_id = d.id"
        " WHERE p.date = :prev_date"
    )
    params_prev = {"prev_date": yesterday_str}
    if district:
        q_prev = text(q_prev.text + " AND d.name_en = :district")
        params_prev["district"] = district
        
    res_prev = await session.execute(q_prev, params_prev)
    prev_prices = {}
    for r in res_prev.mappings().all():
        prev_prices[(r['commodity_id'], r['district'])] = r['price_modal']
        
    # Enrich today_rows with change and trend
    enriched_prices = []
    for r in today_rows:
        commodity_id = r["commodity_id"]
        dist_name = r["district"]
        price_modal = float(r["price_modal"]) if r["price_modal"] is not None else None
        
        change_from_yesterday = None
        change_percent = None
        trend = "flat"
        
        prev_val = prev_prices.get((commodity_id, dist_name))
        if prev_val is not None and price_modal is not None:
            prev_val = float(prev_val)
            change_from_yesterday = round(price_modal - prev_val, 2)
            if prev_val > 0:
                change_percent = round((change_from_yesterday / prev_val) * 100, 2)
            trend = "up" if change_from_yesterday > 0 else ("down" if change_from_yesterday < 0 else "flat")
            
        enriched_prices.append({
            "commodity_id": commodity_id,
            "name_en": r["name_en"],
            "name_ml": r["name_ml"],
            "category": r["category"],
            "unit": r["unit"],
            "district": dist_name,
            "price_min": float(r["price_min"]) if r["price_min"] is not None else None,
            "price_max": float(r["price_max"]) if r["price_max"] is not None else None,
            "price_modal": price_modal,
            "change_from_yesterday": change_from_yesterday,
            "change_percent": change_percent,
            "trend": trend,
            "source": r["source"],
            "date": target_date
        })
        
    return {
        "date": today_str,
        "prices_date": target_date,
        "district": district or "All",
        "prices": enriched_prices,
        "delayed": delayed
    }

@app.get("/api/prices/{commodity_id}/history")
async def commodity_history(commodity_id: str, district: Optional[str] = None, days: int = 30, session: AsyncSession = Depends(get_session)):
    # Find latest date in DB
    res_max = await session.execute(text("SELECT MAX(date) FROM prices"))
    max_date = res_max.scalar()
    if not max_date:
        return {"commodity_id": commodity_id, "history": []}
        
    try:
        if isinstance(max_date, str):
            end = date.fromisoformat(max_date[:10])
        else:
            end = max_date
    except Exception:
        end = date.today()
        
    start = (end - timedelta(days=days)).isoformat()
    
    # Query prices
    params = {"commodity_id": commodity_id, "start": start}
    qtext = "SELECT date, price_modal FROM prices WHERE commodity_id = :commodity_id AND date >= :start"
    if district:
        # resolve district id or name
        dres = await session.execute(text("SELECT id FROM districts WHERE name_en = :name"), {"name": district})
        drow = dres.first()
        if not drow:
            return {"history": []}
        params["district_id"] = drow[0]
        qtext += " AND district_id = :district_id"
    qtext += " ORDER BY date ASC"
    
    res = await session.execute(text(qtext), params)
    rows = []
    for r in res.mappings().all():
        dt = r["date"]
        dt_str = dt.isoformat() if hasattr(dt, 'isoformat') else str(dt)
        rows.append({
            "date": dt_str,
            "price_modal": float(r["price_modal"]) if r["price_modal"] is not None else None
        })
    return {"commodity_id": commodity_id, "history": rows}

@app.get("/api/prices/trending")
async def trending(session: AsyncSession = Depends(get_session)):
    # Find latest date in DB
    res_max = await session.execute(text("SELECT MAX(date) FROM prices"))
    max_date = res_max.scalar()
    if not max_date:
        return {"trending": []}
        
    try:
        if isinstance(max_date, str):
            target_date = date.fromisoformat(max_date[:10])
        else:
            target_date = max_date
    except Exception:
        target_date = date.today()
        
    today_str = target_date.isoformat()
    yesterday_str = (target_date - timedelta(days=1)).isoformat()
    
    q = text(
        "SELECT c.id as commodity_id, c.name_en, c.name_ml, d.name_en as district, p_today.price_modal as today_price, p_y.price_modal as yesterday_price"
        " FROM prices p_today"
        " JOIN commodities c ON p_today.commodity_id = c.id"
        " JOIN districts d ON p_today.district_id = d.id"
        " LEFT JOIN prices p_y ON p_y.commodity_id = p_today.commodity_id AND p_y.district_id = p_today.district_id AND p_y.date = :yesterday"
        " WHERE p_today.date = :today"
    )
    res = await session.execute(q, {"today": today_str, "yesterday": yesterday_str})
    
    rows = []
    for r in res.mappings().all():
        today_price = float(r['today_price']) if r['today_price'] is not None else None
        yesterday_price = float(r['yesterday_price']) if r['yesterday_price'] is not None else None
        
        if today_price is None or yesterday_price is None:
            continue
            
        change = round(today_price - yesterday_price, 2)
        change_percent = None
        if yesterday_price > 0:
            change_percent = round((change / yesterday_price) * 100, 2)
            
        trend = 'up' if change > 0 else ('down' if change < 0 else 'flat')
        rows.append({
            'commodity_id': r['commodity_id'],
            'name_en': r['name_en'],
            'name_ml': r['name_ml'],
            'district': r['district'],
            'today_price': today_price,
            'yesterday_price': yesterday_price,
            'change': change,
            'change_percent': change_percent,
            'trend': trend
        })
        
    # Sort by absolute change percentage desc
    rows.sort(key=lambda x: abs(x['change_percent'] or 0), reverse=True)
    return {'date': today_str, 'trending': rows[:20]}

@app.post("/api/community/submit")
async def submit_community_price(payload: CommunitySubmit, session: AsyncSession = Depends(get_session)):
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL') or ''
    # Verify if commodity and district exist
    res_comm = await session.execute(text("SELECT id FROM commodities WHERE id = :id"), {"id": payload.commodity_id})
    if not res_comm.first():
        raise HTTPException(status_code=400, detail="Invalid commodity_id")
        
    res_dist = await session.execute(text("SELECT id FROM districts WHERE id = :id"), {"id": payload.district_id})
    if not res_dist.first():
        raise HTTPException(status_code=400, detail="Invalid district_id")
        
    price_id = str(uuid.uuid4()) if not DATABASE_URL or 'sqlite' in DATABASE_URL else str(uuid.uuid4())
    
    insert_q = text(
        "INSERT INTO community_prices (id, commodity_id, district_id, price, market_name, verified) "
        "VALUES (:id, :comm_id, :dist_id, :price, :market, :verified)"
    )
    params = {
        "id": price_id,
        "comm_id": payload.commodity_id,
        "dist_id": payload.district_id,
        "price": payload.price,
        "market": payload.market_name,
        "verified": False
    }
    await session.execute(insert_q, params)
    await session.commit()
    return {"status": "success", "id": price_id}

@app.post("/api/alerts")
async def create_alert(payload: AlertCreate, session: AsyncSession = Depends(get_session)):
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL') or ''
    # Verify if commodity and district exist
    res_comm = await session.execute(text("SELECT id FROM commodities WHERE id = :id"), {"id": payload.commodity_id})
    if not res_comm.first():
        raise HTTPException(status_code=400, detail="Invalid commodity_id")
        
    res_dist = await session.execute(text("SELECT id FROM districts WHERE id = :id"), {"id": payload.district_id})
    if not res_dist.first():
        raise HTTPException(status_code=400, detail="Invalid district_id")
        
    alert_id = str(uuid.uuid4()) if not DATABASE_URL or 'sqlite' in DATABASE_URL else str(uuid.uuid4())
    
    insert_q = text(
        "INSERT INTO price_alerts (id, commodity_id, district_id, threshold_price, direction, is_active) "
        "VALUES (:id, :comm_id, :dist_id, :threshold, :direction, :active)"
    )
    params = {
        "id": alert_id,
        "comm_id": payload.commodity_id,
        "dist_id": payload.district_id,
        "threshold": payload.threshold_price,
        "direction": payload.direction,
        "active": True
    }
    await session.execute(insert_q, params)
    await session.commit()
    return {"status": "success", "id": alert_id}

@app.post("/admin/sync")
async def admin_sync():
    """Trigger an immediate sync of prices into DB (if configured)."""
    await tasks.sync_all_prices()
    return {"status": "sync_started"}
