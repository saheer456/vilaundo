from backend.app.scrapers.agmarknet import parse_agmarknet_html
from backend.app.scrapers.horticorp import parse_horticorp_html
import pathlib

FIX = pathlib.Path(__file__).parent / 'fixtures'


def test_agmarknet_parser():
    html = (FIX / 'agmarknet_sample.html').read_text(encoding='utf8')
    res = parse_agmarknet_html(html)
    assert isinstance(res, list)
    assert len(res) == 2
    first = res[0]
    assert first['commodity_name_en'] == 'Black Pepper'
    assert first['district_name_en'] == 'Kozhikode'
    assert first['price_modal'] == 780


def test_horticorp_parser():
    html = (FIX / 'horticorp_sample.html').read_text(encoding='utf8')
    res = parse_horticorp_html(html)
    assert isinstance(res, list)
    assert len(res) == 2
    p = res[0]
    assert p['commodity_name_en'] == 'Potato'
    assert p['price_modal'] == 20
