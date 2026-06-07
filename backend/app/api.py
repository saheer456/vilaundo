from typing import List, Dict, Optional
import asyncio
import logging
from .scrapers.agmarknet import fetch_agmarknet_prices
from .scrapers.horticorp import fetch_horticorp_prices

async def fetch_live_prices(district: Optional[str] = None) -> List[Dict]:
    """Fetch and normalize prices from all scrapers concurrently."""
    tasks = [fetch_agmarknet_prices(district=district), fetch_horticorp_prices()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    records = []
    for res in results:
        if isinstance(res, Exception):
            logging.exception('Scraper error: %s', res)
            continue
        if not res:
            continue
        for r in res:
            # normalize keys to a common shape
            rec = {
                'commodity_name_en': r.get('commodity_name_en') or r.get('commodity') or r.get('name_en'),
                'name_ml': r.get('name_ml') if 'name_ml' in r else None,
                'district_name_en': r.get('district_name_en') or r.get('district'),
                'price_min': r.get('price_min'),
                'price_max': r.get('price_max'),
                'price_modal': r.get('price_modal'),
                'unit': r.get('unit') or 'kg',
                'source': r.get('source'),
                'date': r.get('date')
            }
            records.append(rec)
    return records
