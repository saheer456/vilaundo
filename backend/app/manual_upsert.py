"""
Insert a sample price record into the local sqlite dev.db for testing upsert logic.
Run: python backend/app/manual_upsert.py
"""
import asyncio
from .db import AsyncSessionLocal, engine
from .models import Base
import datetime

async def run():
    # ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy import text
    async with AsyncSessionLocal() as session:
        # find a commodity and a district
        res = await session.execute(text("SELECT id FROM commodities WHERE name_en = :name"), {'name':'Black Pepper'})
        row = res.first()
        if not row:
            print('Commodity not found; run seed first')
            return
        commodity_id = row[0]

        res = await session.execute(text("SELECT id FROM districts WHERE name_en = :name"), {'name':'Kozhikode'})
        row = res.first()
        if not row:
            print('District not found; run seed first')
            return
        district_id = row[0]

        date_val = datetime.date.today().isoformat()
        price_min = 770
        price_max = 790
        price_modal = 780

        # delete existing for date
        await session.execute(text("DELETE FROM prices WHERE commodity_id = :c AND district_id = :d AND date = :dt"),
                              {'c':commodity_id, 'd':district_id, 'dt':date_val})
        await session.execute(
            text("INSERT INTO prices (commodity_id, district_id, price_min, price_max, price_modal, date, source) VALUES (:c,:d,:pmin,:pmax,:pmodal,:dt,:src)"),
            {'c':commodity_id, 'd':district_id, 'pmin':price_min, 'pmax':price_max, 'pmodal':price_modal, 'dt':date_val, 'src':'MANUAL'}
        )
        await session.commit()
        print('Inserted sample price')

if __name__ == '__main__':
    asyncio.run(run())
