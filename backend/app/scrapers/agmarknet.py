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

def parse_agmarknet_html(html: str) -> List[Dict]:
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    tables = soup.find_all('table')
    for table in tables:
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
                data['district'] = cols[1] if len(cols) > 1 else None
                data['price_min'] = cols[2] if len(cols) > 2 else None
                data['price_max'] = cols[3] if len(cols) > 3 else None
                if len(cols) > 4:
                    data['unit'] = cols[4]

            commodity = data.get('commodity') or data.get('commodity name') or data.get('commodity_name')
            district = data.get('district') or data.get('market')
            price_min = _parse_price(data.get('price_min') or data.get('min price') or data.get('min'))
            price_max = _parse_price(data.get('price_max') or data.get('max price') or data.get('max'))
            price_modal = _parse_price(data.get('modal price') or data.get('price') )
            unit = data.get('unit') or data.get('uom') or 'kg'

            if price_modal is None and price_min is not None and price_max is not None:
                try:
                    price_modal = (price_min + price_max) / 2
                except Exception:
                    price_modal = price_min

            if not commodity or not district:
                continue

            results.append({
                'commodity_name_en': commodity,
                'district_name_en': district,
                'price_min': price_min,
                'price_max': price_max,
                'price_modal': price_modal,
                'unit': unit,
                'date': None,
                'source': 'AGMARKNET'
            })
    return results

async def fetch_agmarknet_prices(commodity: str = None, district: str = None) -> List[Dict]:
    URL = "https://agmarknet.gov.in/SearchCommodity.aspx"
    params = {"state": "KL"}
    if commodity:
        params["commodity"] = commodity
    if district:
        params["district"] = district

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(URL, params=params)
        if resp.status_code != 200:
            logging.warning("Agmarknet fetch failed: %s", resp.status_code)
            return []
        return parse_agmarknet_html(resp.text)
