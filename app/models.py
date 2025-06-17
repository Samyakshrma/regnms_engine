from dataclasses import dataclass
from typing import Optional
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Literal


@dataclass
class Order:
    id: str
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market", "limit", "ioc", "fok"
    price: Optional[float]
    quantity: float
    timestamp: datetime

@dataclass
class Trade:
    trade_id: str
    symbol: str
    price: float
    quantity: float
    timestamp: datetime
    maker_order_id: str
    taker_order_id: str
    aggressor_side: str  # "buy" or "sell"

class OrderRequest(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    order_type: Literal["limit", "market"]
    price: Optional[float]  # Required for limit orders
    quantity: float