# Scrapers — VilaUndo

This document describes the web scrapers, how they work, and how to test them locally.

Files
- backend/app/scrapers/agmarknet.py — Agmarknet parser and fetcher
- backend/app/scrapers/horticorp.py — HORTICORP parser and fetcher
- backend/app/api.py — aggregator that runs scrapers concurrently and normalizes output
- backend/app/tasks.py — scheduled sync job that upserts to DB when DATABASE_URL is configured

How the scrapers work
- Each scraper exposes a parse_*_html(html: str) helper that converts HTML to a list of normalized records: {commodity_name_en, district_name_en, price_min, price_max, price_modal, unit, date, source}
- fetch_* functions perform HTTP GETs and call the parser
- Parsers use BeautifulSoup and regex to extract numeric values and handle common table structures

Running locally
1. Run parser unit tests:
   python -m pytest -q backend/tests

2. Trigger live scraping (no DB required):
   Start the backend server: uvicorn backend.app.main:app --reload --port 8000
   Then GET http://127.0.0.1:8000/api/prices/today
   This runs scrapers live and returns consolidated JSON.

3. Manual sync to DB (after setting DATABASE_URL):
   POST http://127.0.0.1:8000/admin/sync

Notes & best practices
- Respect robots.txt and throttle requests. Add delays or caching if needed.
- Use retries with exponential backoff (httpx supports retry hooks or custom logic).
- When integrating DB, perform upserts and store source+timestamp for audit.
- Add more unit tests with real HTML snapshots to cover edge cases.
