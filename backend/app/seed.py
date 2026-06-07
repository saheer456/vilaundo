"""
Simple seed script to populate commodities and districts.
Run with: DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname python backend/app/seed.py
"""
import os
import asyncio
import asyncpg

COMMODITIES = [
    {"name_en": "Black Pepper", "name_ml": "കുരുമുളക്", "category": "spices", "unit": "kg"},
    {"name_en": "Cardamom", "name_ml": "എള്ള്", "category": "spices", "unit": "kg"},
    {"name_en": "Ginger", "name_ml": "ഇഞ്ചി", "category": "spices", "unit": "kg"},
    {"name_en": "Turmeric", "name_ml": "മഞ്ഞൾ", "category": "spices", "unit": "kg"},
    {"name_en": "Coconut", "name_ml": "തേങ്ങ", "category": "coconut", "unit": "piece"},
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

async def run():
    DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    if not DATABASE_URL:
        print('ERROR: Set DATABASE_URL or SUPABASE_DB_URL in environment')
        return

    conn = await asyncpg.connect(DATABASE_URL)
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

        print('Seeding complete')
    finally:
        await conn.close()

if __name__ == '__main__':
    asyncio.run(run())
