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
    {"name_en": "Cardamom", "name_ml": "ഏലം", "category": "spices", "unit": "kg"},
    {"name_en": "Ginger", "name_ml": "ഇഞ്ചി", "category": "spices", "unit": "kg"},
    {"name_en": "Turmeric", "name_ml": "മഞ്ഞൾ", "category": "spices", "unit": "kg"},
    {"name_en": "Coconut", "name_ml": "തേങ്ങ", "category": "coconut", "unit": "kg"},
    {"name_en": "Rubber", "name_ml": "റബ്ബർ", "category": "rubber", "unit": "kg"},
    {"name_en": "Banana", "name_ml": "ഏത്തപ്പഴം", "category": "vegetables", "unit": "kg"},
    {"name_en": "Tapioca", "name_ml": "മരച്ചീനി", "category": "vegetables", "unit": "kg"}
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


BASE_PRICES = {
    "black_pepper": 780.0,
    "cardamom": 1200.0,
    "ginger": 130.0,
    "turmeric": 160.0,
    "coconut": 55.0,
    "rubber": 185.0,
    "banana": 45.0,
    "tapioca": 35.0
}


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
        # Clear existing metadata to refresh translations and units
        await session.execute(text("DELETE FROM commodities"))
        await session.execute(text("DELETE FROM districts"))
        
        for c in COMMODITIES:
            id_val = c['name_en'].lower().replace(' ', '_')
            await session.execute(
                text("INSERT OR REPLACE INTO commodities (id, name_en, name_ml, category, unit) VALUES (:id, :name, :name_ml, :category, :unit)"),
                {'id': id_val, 'name': c['name_en'], 'name_ml': c['name_ml'], 'category': c['category'], 'unit': c['unit']}
            )
        for d in DISTRICTS:
            id_val = d['name_en'].lower().replace(' ', '_')
            await session.execute(
                text("INSERT OR REPLACE INTO districts (id, name_en, name_ml, region) VALUES (:id, :name, :name_ml, :region)"),
                {'id': id_val, 'name': d['name_en'], 'name_ml': d['name_ml'], 'region': d['region']}
            )
        await session.commit()

        # Seed 30 days of prices for SQLite
        import random
        from datetime import date, timedelta
        
        await session.execute(text("DELETE FROM prices"))
        
        for c in COMMODITIES:
            comm_id = c['name_en'].lower().replace(' ', '_')
            base_price = BASE_PRICES.get(comm_id, 100.0)
            for d in DISTRICTS:
                dist_id = d['name_en'].lower().replace(' ', '_')
                
                # Symmetrical drift based on name lengths
                district_offset = (len(d['name_en']) % 5) * 5.0 - 10.0
                current_price = base_price + district_offset
                
                for day_offset in range(30, -1, -1):
                    dt = (date.today() - timedelta(days=day_offset)).isoformat()
                    # random walk
                    current_price = max(1.0, current_price + random.uniform(-3.0, 3.0))
                    price_modal = round(current_price, 2)
                    price_min = round(price_modal * 0.95, 2)
                    price_max = round(price_modal * 1.05, 2)
                    
                    price_id = f"{comm_id}_{dist_id}_{dt}"
                    await session.execute(
                        text("""
                            INSERT OR REPLACE INTO prices (id, commodity_id, district_id, price_min, price_max, price_modal, date, source)
                            VALUES (:id, :c_id, :d_id, :p_min, :p_max, :p_modal, :dt, :src)
                        """),
                        {
                            'id': price_id,
                            'c_id': comm_id,
                            'd_id': dist_id,
                            'p_min': price_min,
                            'p_max': price_max,
                            'p_modal': price_modal,
                            'dt': dt,
                            'src': 'AGMARKNET' if c['category'] != 'vegetables' else 'HORTICORP'
                        }
                    )
        await session.commit()
    await engine.dispose()
    print('SQLite seeding complete with 30-day historical prices')


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

        # Seed Postgres prices
        await conn.execute('DELETE FROM prices') # clear previous prices
        commodities_rows = await conn.fetch('SELECT id, name_en FROM commodities')
        districts_rows = await conn.fetch('SELECT id, name_en FROM districts')
        
        # Maps
        commodities_map = {r['name_en'].lower().replace(' ', '_'): r['id'] for r in commodities_rows}
        districts_map = {r['name_en'].lower().replace(' ', '_'): r['id'] for r in districts_rows}
        
        from datetime import date, timedelta
        import random
        
        price_inserts = []
        for c_key, c_id in commodities_map.items():
            base_price = BASE_PRICES.get(c_key, 100.0)
            category = next((x['category'] for x in COMMODITIES if x['name_en'].lower().replace(' ', '_') == c_key), 'spices')
            src = 'AGMARKNET' if category != 'vegetables' else 'HORTICORP'
            
            for d_key, d_id in districts_map.items():
                d_name = next(x['name_en'] for x in DISTRICTS if x['name_en'].lower().replace(' ', '_') == d_key)
                district_offset = (len(d_name) % 5) * 5.0 - 10.0
                current_price = base_price + district_offset
                
                for day_offset in range(30, -1, -1):
                    dt = date.today() - timedelta(days=day_offset)
                    current_price = max(1.0, current_price + random.uniform(-3.0, 3.0))
                    price_modal = round(current_price, 2)
                    price_min = round(price_modal * 0.95, 2)
                    price_max = round(price_modal * 1.05, 2)
                    
                    price_inserts.append((c_id, d_id, price_min, price_max, price_modal, dt, src))
                    
        # Batch insert into Postgres
        await conn.executemany('''
            INSERT INTO prices (commodity_id, district_id, price_min, price_max, price_modal, date, source)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        ''', price_inserts)
        print('Postgres seeding complete with 30-day historical prices')
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

