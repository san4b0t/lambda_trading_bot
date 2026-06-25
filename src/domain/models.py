from pydantic import BaseModel, Field
from enum import Enum

class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    LIMIT = "limit"
    MARKET = "market"

class Signal(BaseModel):
    symbol: str
    side: Side
    order_type: OrderType
    price: float = Field(gt=0)
    quantity: float = Field(gt=0)

class MarketEvent(BaseModel):
    symbol: str
    price: float = Field(gt=0)
    qty: float = Field(gt=0)
    side: Side