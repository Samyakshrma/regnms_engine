from dataclasses import dataclass
from typing import Optional
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel,  Field, model_validator
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
    price: Optional[float] = Field(default=None)
    quantity: float

    @model_validator(mode="after")
    def check_price_validity(self):
        if self.order_type == "limit" and self.price is None:
            raise ValueError("Price is required for limit orders")
        if self.order_type == "market" and self.price is not None:
            raise ValueError("Price should not be set for market orders")
        return self