# eops/models/rest/order.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from ..common import OrderSide, OrderType

@dataclass(frozen=True)
class Trade:
    id: str
    order_id: str
    eid: str
    symbol: str
    price: float
    amount: float
    side: OrderSide
    timestamp: int
    fee_cost: Optional[float] = None
    fee_currency: Optional[str] = None
    info: Optional[Dict] = None

@dataclass(frozen=True)
class Order:
    id: str
    eid: str
    symbol: str
    timestamp: int
    type: OrderType
    side: OrderSide
    status: str
    amount: float
    filled: float
    cost: float
    client_order_id: Optional[str] = None
    price: Optional[float] = None
    average_price: Optional[float] = None
    trades: List[Trade] = field(default_factory=list)
    info: Optional[Dict] = None