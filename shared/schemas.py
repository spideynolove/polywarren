from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Tick(BaseModel):
    symbol: str
    venue: str
    yes_price: float
    no_price: float
    timestamp: datetime
    volume: Optional[float] = None
    condition_id: Optional[str] = None


class SignalEvent(BaseModel):
    market_id: str
    symbol: str
    venue: str
    trigger_type: str
    value: float
    created_at: datetime


class MarketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    symbol: str
    venue: str
    last_odds: Optional[float]
    updated_at: datetime


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    venue: str
    side: str
    size: float
    status: str
    sent_at: Optional[datetime]
    confirmed_at: Optional[datetime]
    latency_ms: Optional[int]


class PositionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    market_id: str
    venue: str
    side: str
    size: float
    entry_price: float
    opened_at: datetime


class PnLSnapshotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    timestamp: datetime
    value: float
    venue: str
