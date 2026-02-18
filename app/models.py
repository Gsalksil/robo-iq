from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


class ConnectionStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELED = "canceled"
    REJECTED = "rejected"


class MarketTrend(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"


class Candle(BaseModel):
    timestamp: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)

    @field_validator("high")
    @classmethod
    def validate_high(cls, value: float, info):
        if "low" in info.data and value < info.data["low"]:
            raise ValueError("high não pode ser menor que low")
        return value


class ConnectionRequest(BaseModel):
    gmail: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class ConnectionResponse(BaseModel):
    status: ConnectionStatus
    connected_at: datetime | None = None


class OrderRequest(BaseModel):
    symbol: str = Field(min_length=3, max_length=20)
    side: OrderSide
    amount: float = Field(gt=0)
    expiration_seconds: int = Field(default=60, ge=10, le=3600)


class Order(BaseModel):
    id: str
    symbol: str
    side: OrderSide
    amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    reason: str | None = None


class OrderActionResponse(BaseModel):
    order: Order


class MarketSnapshot(BaseModel):
    symbol: str
    current_price: float
    moving_average_fast: float
    moving_average_slow: float
    trend: MarketTrend
    signal: Literal["buy", "sell", "wait"]
    candles: list[Candle]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def new_order_id() -> str:
    return f"ord_{uuid4().hex[:12]}"
