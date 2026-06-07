import os
import sys
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend package is importable when running tests from backend/
# Add project root to sys.path so 'backend' package is importable
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app import seed as seed_mod

# Disable scheduler during tests
os.environ['DISABLE_SCHEDULER'] = '1'


def test_api_endpoints(tmp_path):
    # use isolated sqlite DB per test
    db_file = tmp_path / 'test.db'
    os.environ['DATABASE_URL'] = f'sqlite+aiosqlite:///{db_file}'

    # seed db
    asyncio.run(seed_mod.run())

    from backend.app.main import app
    with TestClient(app) as client:
        r = client.get('/api/commodities')
        assert r.status_code == 200
        data = r.json()
        assert 'commodities' in data and len(data['commodities']) > 0

        r2 = client.get('/api/prices/today')
        assert r2.status_code == 200
        data2 = r2.json()
        assert 'date' in data2 and 'prices' in data2
