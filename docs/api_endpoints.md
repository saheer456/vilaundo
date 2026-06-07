# API Endpoints (required)

Core APIs for VilaUndo MVP — implement these on the backend.

GET /api/prices/today
- Query: ?district=Kozhikode
- Returns: { date, district, prices: [{commodity_name_en, name_ml?, district_name_en, unit, price_min, price_max, price_modal, source, date}] }
- Behavior: If DB available, read today's prices; otherwise scrape live.

GET /api/commodities
- Returns list of commodities (id, name_en, name_ml, category, unit)

GET /api/districts
- Returns list of Kerala districts (id, name_en, name_ml, region)

GET /api/prices/{commodity_id}/history
- Params: ?district= & ?days=30
- Returns: time series of price points

POST /api/community/submit
- Body: { commodity_id | commodity_name, district_id | district_name, price, market_name, submitted_by (optional) }
- Behavior: store in community_prices table (marked unverified)

POST /api/alerts
- Create price alert for user (requires auth later)

GET /api/prices/trending
- Top movers today (Δ vs yesterday)

Admin /sync
POST /admin/sync
- Triggers immediate scrape and upsert to DB (requires DATABASE_URL)

Notes for implementation
- All endpoints should include source attribution and timestamp per price record.
- Support district and category filters for list endpoints.
- Implement pagination for commodity lists.
- Protect admin endpoints behind auth in production.

Client-side expectations
- Prices endpoint should respond <2s in typical case. Use caching (Redis) for scraped results.
- Return consistent numeric types for prices (numbers, not strings).
