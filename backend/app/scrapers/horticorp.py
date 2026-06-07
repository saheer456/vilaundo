import httpx
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

DISTRICT_MAP = {
    'tvm': 'Thiruvananthapuram',
    'klm': 'Kollam',
    'alp': 'Alappuzha',
    'pta': 'Pathanamthitta',
    'ktm': 'Kottayam',
    'ekm': 'Ernakulam',
    'tsr': 'Thrissur',
    'idk': 'Idukki',
    'mlpm': 'Malappuram',
    'kkd': 'Kozhikode',
    'plkd': 'Palakkad',
    'knr': 'Kannur'
}

CROP_MAP = {
    'BANANA FRUIT': 'Banana',
    'RAW BANANA': 'Banana',
    'PALAYANTHODAN': 'Banana',
    'TAPIOCA': 'Tapioca',
    'GINGER': 'Ginger',
    'COCONUT': 'Coconut'
}

def parse_horticorp_html(html: str) -> List[Dict]:
    """Parse horticorp price table from horticorp.org (new) or price-table (old sample)."""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='price-table') or soup.find('table')
    results = []
    if not table:
        return results
        
    rows = table.find_all('tr')
    if not rows:
        return results
        
    headers = [th.get_text(strip=True).lower() for th in rows[0].find_all(['th', 'td'])]
    is_district_table = 'items' in headers or 's.no' in headers or any(h in DISTRICT_MAP for h in headers)
    
    if is_district_table:
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if not cols or len(cols) < 2:
                continue
                
            raw_crop_name = cols[1].strip().upper()
            matched_crop = None
            for key, val in CROP_MAP.items():
                if key in raw_crop_name:
                    matched_crop = val
                    break
                    
            if not matched_crop:
                continue
                
            for i, header in enumerate(headers):
                if header in DISTRICT_MAP:
                    dist_name = DISTRICT_MAP[header]
                    price_str = cols[i].strip() if i < len(cols) else ""
                    if not price_str:
                        continue
                    try:
                        price_val = float(price_str.replace(',', ''))
                        if price_val <= 0:
                            continue
                            
                        results.append({
                            'commodity_name_en': matched_crop,
                            'district_name_en': dist_name,
                            'price_min': round(price_val * 0.95, 2),
                            'price_max': round(price_val * 1.05, 2),
                            'price_modal': price_val,
                            'unit': 'kg',
                            'date': None,
                            'source': 'HORTICORP'
                        })
                    except Exception:
                        pass
    else:
        # Fallback for old 3-column table
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if not cols or len(cols) < 3:
                continue
            commodity = cols[0].strip()
            try:
                price_min = float(cols[1].strip())
                price_max = float(cols[2].strip())
                price_modal = (price_min + price_max) / 2
                results.append({
                    'commodity_name_en': commodity,
                    'district_name_en': None,
                    'price_min': price_min,
                    'price_max': price_max,
                    'price_modal': price_modal,
                    'unit': 'kg',
                    'date': None,
                    'source': 'HORTICORP'
                })
            except Exception:
                pass
                
    return results

async def fetch_horticorp_prices() -> List[Dict]:
    URL = "https://horticorp.org/price-list/"
    async with httpx.AsyncClient(timeout=20, verify=False) as client:
        try:
            resp = await client.get(URL)
            if resp.status_code != 200:
                logging.warning("HORTICORP fetch failed: %s", resp.status_code)
                return []
            return parse_horticorp_html(resp.text)
        except Exception as e:
            logging.exception("Horticorp request failed: %s", e)
            return []
