import httpx
from bs4 import BeautifulSoup
import logging
import re
from typing import List, Dict

PRICE_RE = re.compile(r"[\d,.]+")

def _parse_price(s: str):
    if s is None:
        return None
    m = PRICE_RE.search(s.replace('\u00a0', ' '))
    if not m:
        return None
    val = m.group(0).replace(',', '')
    try:
        return float(val)
    except Exception:
        return None


def parse_horticorp_html(html: str) -> List[Dict]:
    """Parse horticorp price page (looks for table.price-table)."""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='price-table') or soup.find('table')
    results = []
    if not table:
        return results
    headers = [th.get_text(strip=True).lower() for th in table.find_all('th')]
    rows = table.find_all('tr')
    for row in rows[1:]:
        cols = [td.get_text(strip=True) for td in row.find_all(['td','th'])]
        if not cols:
            continue
        data = {}
        if headers and len(headers) == len(cols):
            for i, h in enumerate(headers):
                data[h] = cols[i]
        else:
            data['commodity'] = cols[0] if len(cols) > 0 else None
            data['price_min'] = cols[1] if len(cols) > 1 else None
            data['price_max'] = cols[2] if len(cols) > 2 else None

        commodity = data.get('commodity') or data.get('item')
        price_min = _parse_price(data.get('price_min') or data.get('min'))
        price_max = _parse_price(data.get('price_max') or data.get('max'))
        unit = data.get('unit') or 'kg'

        if price_min is None and price_max is None:
            continue
        price_modal = price_min if price_min is not None else price_max
        try:
            if price_min is not None and price_max is not None:
                price_modal = (price_min + price_max)/2
        except Exception:
            pass

        results.append({
            'commodity_name_en': commodity,
            'district_name_en': None,
            'price_min': price_min,
            'price_max': price_max,
            'price_modal': price_modal,
            'unit': unit,
            'date': None,
            'source': 'HORTICORP'
        })
    return results

async def fetch_horticorp_prices() -> List[Dict]:
    URL = "https://horticorp.com/price-of-vegetables"
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(URL)
        if resp.status_code != 200:
            logging.warning("HORTICORP fetch failed: %s", resp.status_code)
            return []
        return parse_horticorp_html(resp.text)
