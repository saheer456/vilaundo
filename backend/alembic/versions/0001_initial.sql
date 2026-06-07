-- Initial schema migration for VilaUndo

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE commodities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_en TEXT NOT NULL,
    name_ml TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_en TEXT NOT NULL,
    name_ml TEXT NOT NULL,
    region TEXT
);

CREATE TABLE prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id UUID REFERENCES commodities(id),
    district_id UUID REFERENCES districts(id),
    price_min NUMERIC(10,2),
    price_max NUMERIC(10,2),
    price_modal NUMERIC(10,2),
    date DATE NOT NULL,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (commodity_id, district_id, date)
);

CREATE TABLE community_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id UUID REFERENCES commodities(id),
    district_id UUID REFERENCES districts(id),
    price NUMERIC(10,2) NOT NULL,
    market_name TEXT,
    submitted_by UUID,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    commodity_id UUID REFERENCES commodities(id),
    district_id UUID REFERENCES districts(id),
    threshold_price NUMERIC(10,2),
    direction TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prices_date ON prices(date DESC);
CREATE INDEX idx_prices_commodity ON prices(commodity_id);
CREATE INDEX idx_prices_district ON prices(district_id);
