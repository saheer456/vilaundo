from sqlalchemy import Column, String, Text, Date, Numeric, Boolean, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Commodity(Base):
    __tablename__ = 'commodities'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    name_en = Column(String, nullable=False)
    name_ml = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class District(Base):
    __tablename__ = 'districts'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    name_en = Column(String, nullable=False)
    name_ml = Column(String, nullable=False)
    region = Column(String)

class Price(Base):
    __tablename__ = 'prices'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    commodity_id = Column(UUID(as_uuid=True), ForeignKey('commodities.id'))
    district_id = Column(UUID(as_uuid=True), ForeignKey('districts.id'))
    price_min = Column(Numeric(10,2))
    price_max = Column(Numeric(10,2))
    price_modal = Column(Numeric(10,2))
    date = Column(Date, nullable=False)
    source = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class CommunityPrice(Base):
    __tablename__ = 'community_prices'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    commodity_id = Column(UUID(as_uuid=True), ForeignKey('commodities.id'))
    district_id = Column(UUID(as_uuid=True), ForeignKey('districts.id'))
    price = Column(Numeric(10,2), nullable=False)
    market_name = Column(String)
    submitted_by = Column(UUID(as_uuid=True))
    verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class PriceAlert(Base):
    __tablename__ = 'price_alerts'
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()'))
    user_id = Column(UUID(as_uuid=True))
    commodity_id = Column(UUID(as_uuid=True), ForeignKey('commodities.id'))
    district_id = Column(UUID(as_uuid=True), ForeignKey('districts.id'))
    threshold_price = Column(Numeric(10,2))
    direction = Column(String)
    is_active = Column(Boolean, server_default=text('true'))
    last_triggered = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
