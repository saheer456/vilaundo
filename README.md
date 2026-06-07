# VilaUndo (വിലുണ്ടോ) 🌾📈

[![Build and Test Status](https://img.shields.io/badge/status-active-emerald.svg)](https://github.com/saheer456/vilaundo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Bilingual](https://img.shields.io/badge/language-മലയാളം%20%2F%20English-teal.svg)](#localization)

**VilaUndo (വിലുണ്ടോ)** is a premium, real-time bilingual daily agricultural price tracker and dashboard custom-tailored for farmers, traders, and consumers in Kerala, India. Meaning *"Is there a price?"* in Malayalam, VilaUndo connects users directly to official market rates, removing middlemen asymmetry and keeping agricultural trade transparent.

---

## 🚀 Key Features

*   **Bilingual Localization:** Fully localized dashboard supporting English and Malayalam (**മലയാളം**), including accurate regional names for commodities (e.g., *തേങ്ങ* for coconut, *ഏത്തപ്പഴം* for banana, *മരച്ചീനി* for tapioca).
*   **Kerala Gov Price Feed Scraper:** Real-time data sync with the official Kerala Government portal ([Horticorp Price List](https://horticorp.org/price-list/)), providing official daily market rates across all 14 districts.
*   **Consistent Units:** All crops are standardly configured to display prices in **per kg** (e.g., converting coconuts from piece/dozen to standard per kg rates).
*   **Global Commodity Ticker:** A live exchange-rate commodity ticker pulling spot rates for Rubber, Black Pepper, and Cardamom. It automatically fetches keyless exchange rates from the `Open Exchange Rate API` to convert global USD rates to local INR per kg.
*   **Interactive Price Visualization:** Visual trend badges and price change history graphs.
*   **District-wise Filters & Geolocation:** Custom district selection with coordinates-based district recommendations.
*   **Crowdsourced Pricing & Alerts:** Community price reporting system and threshold-based notification alerts.
*   **SEO Optimized:** Ready for production deployment with comprehensive meta descriptions, Open Graph/Twitter card attributes, and HTML5 semantic hierarchy.

---

## 🛠️ Technology Stack

### Backend
*   **Framework:** FastAPI (Python 3.10+)
*   **Database:** SQLAlchemy ORM with multi-dialect support (SQLite for local development `dev.db`, PostgreSQL for production/Supabase).
*   **Scheduler & Worker:** Background sync task using raw SQL `text()` queries for absolute database compatibility.
*   **Scraping:** BeautifulSoup4 for Horticorp Kerala Gov parsing.

### Frontend
*   **Framework:** React 18+ (Vite)
*   **Styling:** TailwindCSS + Vanilla CSS transitions
*   **State Management:** Zustand
*   **Internationalization:** i18next

---

## 📁 Repository Structure

```text
VilaUndo/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app endpoints and config
│   │   ├── database.py          # SQLAlchemy connection & DB session
│   │   ├── models.py            # SQLite/PostgreSQL shared schemas
│   │   ├── seed.py              # Initial crop metadata & district database seeds
│   │   ├── tasks.py             # Scheduled database price synchronization
│   │   └── scrapers/
│   │       └── horticorp.py     # Live Kerala Gov Horticorp scraper
│   └── tests/                   # Backend scraper and endpoint unit tests
└── frontend/
    ├── public/
    │   ├── logo.png             # Modern VilaUndo application logo asset
    │   └── favicon.png          # App shortcut icon
    ├── src/
    │   ├── App.jsx              # Main dashboard entrypoint & layout
    │   ├── components/          # Reusable UI widgets (Ticker, Selector, Cards)
    │   ├── store/               # Zustand state stores
    │   └── i18n/                # Malayalam & English translation catalogs
    ├── index.html               # Main SEO-tagged HTML shell
    └── package.json
```

---

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.10+
*   Node.js 18+ & npm
*   Git

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy env variables template:
   ```bash
   cp ../env.example .env
   ```
5. Initialize and seed the local database:
   ```bash
   python -m app.seed
   ```
6. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## 🧪 Running Tests

### Backend Unit Tests
VilaUndo contains test suites for data integrity, Horticorp scraper logic, and endpoints. To execute tests:
```bash
cd backend
python -m pytest
```

### Production Build
To test the optimized production build of the React bundle:
```bash
cd frontend
npm run build
```

---

## 🔒 License
This project is licensed under the MIT License - see the LICENSE file for details.
