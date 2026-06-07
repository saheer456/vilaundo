# VilaUndo (വിലുണ്ടോ) — Kerala Farm Price Tracker
### Development Plan & Technical Reference

> A Kerala-first web platform for real-time prices of locally grown commodities — spices, coconut, rubber, vegetables — built for farmers, traders, and everyday buyers.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Target Users](#2-target-users)
3. [Core Features](#3-core-features)
4. [Tech Stack](#4-tech-stack)
5. [System Architecture](#5-system-architecture)
6. [Data Sources & Pipeline](#6-data-sources--pipeline)
7. [Database Schema](#7-database-schema)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend Structure](#9-frontend-structure)
10. [Phase Roadmap](#10-phase-roadmap)
11. [Deployment](#11-deployment)
12. [Monetization Ideas](#12-monetization-ideas)

---

## 1. Project Overview

**Project Name:** VilaUndo (വിലുണ്ടോ)
**Tagline:** *Kerala's daily price companion for farmers and buyers*
**Language:** Bilingual — Malayalam + English
**Primary Platform:** Mobile-first web app (PWA)

### Problem Statement

Kerala farmers and small traders currently rely on:
- WhatsApp forwards (often outdated or wrong)
- Physical market visits just to check prices
- Government portals (Agmarknet) that are desktop-heavy and non-intuitive

VilaUndo solves this by providing clean, fast, district-wise daily prices with trend data — accessible on any smartphone.

---

## 2. Target Users

| User Type | Need |
|---|---|
| Small farmers | Know today's mandi price before selling |
| Traders / middlemen | Compare prices across districts |
| Homemakers / buyers | Know vegetable/coconut prices locally |
| Agri-businesses | Trend data for procurement decisions |

---

## 3. Core Features

### Phase 1 — MVP
- Daily prices for 50+ Kerala commodities
- District-wise filtering (14 districts)
- Price trend indicator (↑ / ↓ vs yesterday)
- Malayalam + English labels for all crops
- Mobile-first responsive UI
- WhatsApp share button per item

### Phase 2 — Growth
- Price history charts (7-day, 30-day)
- Price alerts via browser push notifications
- User location auto-detect → default district
- Community price submissions (crowdsourcing layer)
- Search bar with Malayalam input support

### Phase 3 — Sticky & Monetized
- Farmer accounts — track your own crops
- Price forecast (ML-based, 7-day outlook)
- Export price data as CSV/PDF
- Aggregator/NGO API access (paid tier)
- WhatsApp bot integration

---

## 4. Tech Stack

### Frontend
| Layer | Technology | Reason |
|---|---|---|
| Framework | React 18 + Vite | Fast builds, familiar stack |
| Styling | Tailwind CSS | Utility-first, mobile-friendly |
| State | Zustand | Lightweight, no boilerplate |
| Data fetching | TanStack Query | Caching, auto-refresh |
| Charts | Recharts | Simple, React-native |
| i18n | react-i18next | Malayalam/English switching |
| PWA | Vite PWA plugin | Offline support, installable |

### Backend
| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI (Python) | Async, fast, familiar |
| ORM | SQLAlchemy + Alembic | Migrations, type-safe |
| Task queue | APScheduler | Cron jobs for data sync |
| Scraping | httpx + BeautifulSoup4 | Lightweight scraping |
| Cache | Redis | Price data caching (TTL 1hr) |

### Database & Infra
| Layer | Technology |
|---|---|
| Primary DB | Supabase (PostgreSQL) |
| Auth | Supabase Auth |
| File storage | Supabase Storage |
| Hosting (frontend) | Vercel |
| Hosting (backend) | Railway or Render |
| Cache | Redis Cloud (free tier) |

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────┐
│                  Data Sources                   │
│  Agmarknet API  │  HORTICORP  │  Community Sub  │
└────────┬────────┴──────┬──────┴────────┬────────┘
         │               │               │
         └───────────────▼───────────────┘
                  ┌──────────────┐
                  │  Data Sync   │  ← APScheduler cron
                  │  (FastAPI)   │    runs daily at 7 AM
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │  Supabase DB │  ← PostgreSQL
                  │  (prices,    │
                  │   history,   │
                  │   districts) │
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │  FastAPI     │  ← REST API
                  │  Backend     │
                  └──────┬───────┘
                         │
                  ┌──────▼───────┐
                  │  React PWA   │  ← Vercel CDN
                  │  (VilaUndo) │
                  └──────────────┘
```

---

## 6. Data Sources & Pipeline

### Primary Source — Agmarknet (Government API)

**Base URL:** `https://agmarknet.gov.in`
**Data portal:** `https://data.gov.in` (Open Government Data)

```python
# Example fetch from Agmarknet daily price endpoint
import httpx

AGMARKNET_URL = "https://agmarknet.gov.in/SearchCommodity.aspx"

KERALA_STATE_CODE = "KL"

COMMODITIES = [
    "Pepper", "Cardamom", "Ginger", "Turmeric",
    "Coconut", "Copra", "Rubber", "Nutmeg",
    "Cloves", "Tapioca", "Banana", "Arecanut"
]

async def fetch_agmarknet_prices(commodity: str, district: str):
    params = {
        "state": KERALA_STATE_CODE,
        "commodity": commodity,
        "district": district,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(AGMARKNET_URL, params=params, timeout=15)
        return parse_agmarknet_response(response.text)
```

### Secondary Source — HORTICORP (Kerala Vegetables)

**URL:** `https://horticorp.com/price-of-vegetables`
Scrape daily vegetable prices published on this page.

```python
from bs4 import BeautifulSoup
import httpx

async def fetch_horticorp_prices():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://horticorp.com/price-of-vegetables")
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table", class_="price-table")
        # Parse rows into price records
        rows = table.find_all("tr")[1:]
        prices = []
        for row in rows:
            cols = row.find_all("td")
            prices.append({
                "commodity": cols[0].text.strip(),
                "price_min": float(cols[1].text.strip()),
                "price_max": float(cols[2].text.strip()),
                "unit": "kg",
                "source": "HORTICORP"
            })
        return prices
```

### Cron Schedule (APScheduler)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Daily sync at 7:30 AM IST
scheduler.add_job(sync_all_prices, "cron", hour=7, minute=30, timezone="Asia/Kolkata")

# Hourly cache refresh
scheduler.add_job(refresh_cache, "interval", hours=1)

scheduler.start()
```

---

## 7. Database Schema

```sql
-- Commodities master table
CREATE TABLE commodities (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_en     TEXT NOT NULL,          -- "Black Pepper"
    name_ml     TEXT NOT NULL,          -- "കുരുമുളക്"
    category    TEXT NOT NULL,          -- "spices" | "vegetables" | "coconut" | "rubber"
    unit        TEXT NOT NULL,          -- "kg" | "piece" | "litre"
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Districts of Kerala
CREATE TABLE districts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_en     TEXT NOT NULL,          -- "Kozhikode"
    name_ml     TEXT NOT NULL,          -- "കോഴിക്കോട്"
    region      TEXT                    -- "North" | "Central" | "South"
);

-- Daily prices (main table)
CREATE TABLE prices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id    UUID REFERENCES commodities(id),
    district_id     UUID REFERENCES districts(id),
    price_min       NUMERIC(10, 2),
    price_max       NUMERIC(10, 2),
    price_modal     NUMERIC(10, 2),     -- most common price
    date            DATE NOT NULL,
    source          TEXT,               -- "AGMARKNET" | "HORTICORP" | "COMMUNITY"
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (commodity_id, district_id, date)
);

-- Community submitted prices (crowdsource)
CREATE TABLE community_prices (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id    UUID REFERENCES commodities(id),
    district_id     UUID REFERENCES districts(id),
    price           NUMERIC(10, 2) NOT NULL,
    market_name     TEXT,
    submitted_by    UUID,               -- anonymous or user ID
    verified        BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Price alerts (Phase 2)
CREATE TABLE price_alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID,
    commodity_id    UUID REFERENCES commodities(id),
    district_id     UUID REFERENCES districts(id),
    threshold_price NUMERIC(10, 2),
    direction       TEXT,               -- "above" | "below"
    is_active       BOOLEAN DEFAULT TRUE,
    last_triggered  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_prices_date ON prices(date DESC);
CREATE INDEX idx_prices_commodity ON prices(commodity_id);
CREATE INDEX idx_prices_district ON prices(district_id);
```

---

## 8. API Endpoints

### FastAPI Backend

```
GET  /api/prices/today                  → All today's prices
GET  /api/prices/today?district=KZD     → Filtered by district
GET  /api/prices/today?category=spices  → Filtered by category
GET  /api/prices/{commodity_id}/history → 30-day price history
GET  /api/commodities                   → All commodities list
GET  /api/districts                     → All 14 Kerala districts
POST /api/community/submit              → Submit a local price
POST /api/alerts                        → Create a price alert
GET  /api/prices/trending               → Top movers today (↑↓)
```

### Example Response — `/api/prices/today`

```json
{
  "date": "2026-06-07",
  "district": "Kozhikode",
  "prices": [
    {
      "commodity_id": "uuid",
      "name_en": "Black Pepper",
      "name_ml": "കുരുമുളക്",
      "category": "spices",
      "unit": "kg",
      "price_min": 770,
      "price_max": 790,
      "price_modal": 780,
      "change_from_yesterday": 12,
      "change_percent": 1.56,
      "trend": "up",
      "source": "AGMARKNET"
    }
  ]
}
```

---

## 9. Frontend Structure

```
src/
├── components/
│   ├── PriceCard.jsx          ← Individual commodity card
│   ├── PriceList.jsx          ← Scrollable list of prices
│   ├── TrendBadge.jsx         ← ↑ / ↓ / → badge
│   ├── DistrictSelector.jsx   ← District dropdown
│   ├── CategoryFilter.jsx     ← Spices / Coconut / etc pills
│   ├── PriceChart.jsx         ← 7-day sparkline chart
│   └── ShareButton.jsx        ← WhatsApp share
│
├── pages/
│   ├── Home.jsx               ← Main price dashboard
│   ├── Commodity.jsx          ← Single item detail + history
│   ├── Alerts.jsx             ← Price alert management
│   └── About.jsx
│
├── store/
│   └── useAppStore.js         ← Zustand: district, filters, lang
│
├── hooks/
│   ├── usePrices.js           ← TanStack Query: fetch prices
│   └── useDistrict.js         ← Geolocation → district
│
├── i18n/
│   ├── en.json                ← English strings
│   └── ml.json                ← Malayalam strings
│
└── utils/
    ├── formatPrice.js         ← ₹ formatting
    └── whatsappShare.js       ← Share message builder
```

### WhatsApp Share Utility

```javascript
// utils/whatsappShare.js
export function buildShareMessage(item, district) {
  return encodeURIComponent(
    `📊 *VilaUndo — Today's Price*\n` +
    `🌿 ${item.name_en} (${item.name_ml})\n` +
    `📍 ${district}\n` +
    `💰 ₹${item.price_modal} per ${item.unit}\n` +
    `📈 ${item.trend === "up" ? "↑" : "↓"} ₹${Math.abs(item.change_from_yesterday)} vs yesterday\n\n` +
    `Check live prices → vilaundo.app`
  );
}

export function shareOnWhatsApp(item, district) {
  const message = buildShareMessage(item, district);
  window.open(`https://wa.me/?text=${message}`, "_blank");
}
```

---

## 10. Phase Roadmap

### Phase 1 — MVP (4–6 weeks)
- [ ] Set up Supabase schema + seed data
- [ ] Build FastAPI backend with Agmarknet + HORTICORP scrapers
- [ ] APScheduler daily cron at 7:30 AM IST
- [ ] React frontend — home page, filters, price cards
- [ ] District selector + localStorage persistence
- [ ] WhatsApp share button
- [ ] Deploy on Vercel (frontend) + Railway (backend)
- [ ] Basic SEO — meta tags in Malayalam + English

### Phase 2 — Growth (6–10 weeks)
- [ ] Price history charts with Recharts
- [ ] Browser push notifications for price alerts
- [ ] Community price submission form
- [ ] Geolocation → auto district detection
- [ ] Malayalam keyboard search support
- [ ] PWA installable (offline caching for last-seen prices)
- [ ] Social sharing image (OG card per commodity)

### Phase 3 — Monetization (10–16 weeks)
- [ ] Farmer accounts (Supabase Auth)
- [ ] Personal watchlist — track your crops
- [ ] 7-day price forecast (Prophet / simple ML model)
- [ ] WhatsApp bot via Twilio or WhatsApp Cloud API
- [ ] API access tier for agri-businesses
- [ ] CSV/PDF export of historical data

---

## 11. Deployment

### Frontend (Vercel)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Railway)
```bash
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```env
# Backend
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_service_role_key
REDIS_URL=redis://...
AGMARKNET_STATE_CODE=KL

# Frontend
VITE_API_URL=https://api.vilaundo.app
VITE_SUPABASE_URL=https://xxxx.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 12. Monetization Ideas

| Model | Description | Potential |
|---|---|---|
| API access (B2B) | Agri-businesses pay for historical data & bulk access | ₹2,000–10,000/month per client |
| Featured listings | Agri-input companies sponsor crop categories | Low-key, non-intrusive |
| WhatsApp bot (premium) | Daily price digest on WhatsApp for ₹29/month | High volume, Kerala-native channel |
| Government grants | Kerala Startup Mission (KSUM) agri-tech grants | Non-dilutive funding |
| NGO/cooperative data | Sell anonymised trend data to farmer cooperatives | Project-based |

---

## Notes & Gotchas

- **Agmarknet reliability:** The government API goes down sometimes. Build a fallback to use the last known price with a "data may be delayed" warning in the UI.
- **Price accuracy:** Display source and timestamp for every price. Builds trust. Never show stale data without a warning.
- **Malayalam font:** Use `Noto Sans Malayalam` from Google Fonts — best coverage, free, fast-loading.
- **Mobile first:** 80%+ of Kerala users will open this on a mid-range Android. Keep JS bundle under 150KB gzipped. Lazy-load charts.
- **District names:** Use official Kerala government spelling for both English and Malayalam to match Agmarknet codes exactly.

---

*Generated: June 2026 · Project: VilaUndo (വിലുണ്ടോ)*
