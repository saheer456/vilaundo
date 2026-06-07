"""
Seed script supporting asyncpg (Postgres) and a local sqlite+aiosqlite fallback using SQLAlchemy.

Run with:
  DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname python backend/app/seed.py
or
  python backend/app/seed.py  # uses local sqlite dev.db
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base, Commodity, District

COMMODITIES = [
    {"name_en": "Black Pepper", "name_ml": "കുരുമുളക്", "category": "spices", "unit": "kg"},
    {"name_en": "Cardamom", "name_ml": "എള്ള്", "category": "spices", "unit": "kg"},
    {"name_en": "Ginger", "name_ml": "ഇഞ്ചി", "category": "spices", "unit": "kg"},
    {"name_en": "Turmeric", "name_ml": "മഞ്ഞൾ", "category": "spices", "unit": "kg"},
    {"name_en": "Coconut", "name_ml": "തേതങ്", "category": "coconut", "unit": "piece"},
    {"name_en": "Rubber", "name_ml": "റബ്ബർ", "category": "rubber", "unit": "kg"},
    {"name_en": "Banana", "name_ml": "വഴുതന", "category": "vegetables", "unit": "dozen"},
    {"name_en": "Tapioca", "name_ml": "കക്കരിപ്പഴം", "category": "vegetables", "unit": "kg"}
]

DISTRICTS = [
    {"name_en": "Thiruvananthapuram", "name_ml": "തിരുവനന്തപുരം", "region": "South"},
    {"name_en": "Kollam", "name_ml": "കൊല്ലം", "region": "South"},
    {"name_en": "Pathanamthitta", "name_ml": "പത്തനംതിട്ട", "region": "South"},
    {"name_en": "Alappuzha", "name_ml": "ആലപ്പുഴ", "region": "Central"},
    {"name_en": "Kottayam", "name_ml": "കോട്ടയം", "region": "Central"},
    {"name_en": "Idukki", "name_ml": "ഇടുക്കി", "region": "Central"},
    {"name_en": "Ernakulam", "name_ml": "എറണാകുളം", "region": "Central"},
    {"name_en": "Thrissur", "name_ml": "തൃശ്ശൂർ", "region": "Central"},
    {"name_en": "Palakkad", "name_ml": "പാലക്കാട്", "region": "North"},
    {"name_en": "Malappuram", "name_ml": "മലപ്പുറം", "region": "North"},
    {"name_en": "Kozhikode", "name_ml": "കോഴിക്കോട്", "region": "North"},
    {"name_en": "Wayanad", "name_ml": "വയനാട്", "region": "North"},
    {"name_en": "Kannur", "name_ml": "കണ്ണൂർ", "region": "North"},
    {"name_en": "Kasargod", "name_ml": "കാസർഗോഡ്", "region": "North"}
]


async def seed_sqlite(db_url: str):
    engine = create_async_engine(db_url, echo=False, future=True)
    from sqlalchemy import text
    async with engine.begin() as conn:
        # Create sqlite-compatible tables with simple types and no Postgres-specific defaults
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS commodities (
                id TEXT PRIMARY KEY,
                name_en TEXT NOT NULL UNIQUE,
                name_ml TEXT,
                category TEXT,
                unit TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS districts (
                id TEXT PRIMARY KEY,
                name_en TEXT NOT NULL UNIQUE,
                name_ml TEXT,
                region TEXT
            );
        '''))
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS prices (
                id TEXT PRIMARY KEY,
                commodity_id TEXT,
                district_id TEXT,
                price_min NUMERIC,
                price_max NUMERIC,
                price_modal NUMERIC,
                date DATE NOT NULL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS community_prices (
                id TEXT PRIMARY KEY,
                commodity_id TEXT,
                district_id TEXT,
                price NUMERIC,
                market_name TEXT,
                submitted_by TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))
        await conn.execute(text('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                commodity_id TEXT,
                district_id TEXT,
                threshold_price NUMERIC,
                direction TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_triggered TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        '''))

    AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        for c in COMMODITIES:
            id_val = c['name_en'].lower().replace(' ', '_')
            await session.execute(
                text("INSERT OR IGNORE INTO commodities (id, name_en, name_ml, category, unit) VALUES (:id, :name, :name_ml, :category, :unit)"),
                {'id': id_val, 'name': c['name_en'], 'name_ml': c['name_ml'], 'category': c['category'], 'unit': c['unit']}
            )
        for d in DISTRICTS:
            id_val = d['name_en'].lower().replace(' ', '_')
            await session.execute(
                text("INSERT OR IGNORE INTO districts (id, name_en, name_ml, region) VALUES (:id, :name, :name_ml, :region)"),
                {'id': id_val, 'name': d['name_en'], 'name_ml': d['name_ml'], 'region': d['region']}
            )
        await session.commit()
    await engine.dispose()
    print('SQLite seeding complete')


async def seed_postgres(db_url: str):
    import asyncpg
    conn = await asyncpg.connect(db_url)
    try:
        for c in COMMODITIES:
            await conn.execute('''
                INSERT INTO commodities (name_en, name_ml, category, unit)
                SELECT $1, $2, $3, $4
                WHERE NOT EXISTS (SELECT 1 FROM commodities WHERE name_en = $1)
            ''', c['name_en'], c['name_ml'], c['category'], c['unit'])
        for d in DISTRICTS:
            await conn.execute('''
                INSERT INTO districts (name_en, name_ml, region)
                SELECT $1, $2, $3
                WHERE NOT EXISTS (SELECT 1 FROM districts WHERE name_en = $1)
            ''', d['name_en'], d['name_ml'], d['region'])
        print('Postgres seeding complete')
    finally:
        await conn.close()


async def run():
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if not DATABASE_URL:
        # use local sqlite dev.db
        sqlite_url = 'sqlite+aiosqlite:///./dev.db'
        await seed_sqlite(sqlite_url)
        return

    if DATABASE_URL.startswith('sqlite') or DATABASE_URL.startswith('sqlite+aiosqlite'):
        await seed_sqlite(DATABASE_URL)
    else:
        await seed_postgres(DATABASE_URL)


if __name__ == '__main__':
    asyncio.run(run())
