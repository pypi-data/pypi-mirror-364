# eops/models.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Import from the new instruments module
from .instruments import Instrument

# This file defines unified, framework-wide data structures for various exchange objects.

@dataclass(frozen=True)
class Kline:
    """Unified representation of a single OHLCV candle."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: Optional[float] = None

@dataclass(frozen=True)
class Balance:
    """Unified representation of a single asset's balance."""
    asset: str
    total: float
    available: float

@dataclass(frozen=True)
class Position:
    """Unified representation of a trading position."""
    eid: str
    amount: float
    side: str
    entry_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    leverage: Optional[float] = None
    info: Optional[Dict] = None

@dataclass(frozen=True)
class Trade:
    """Unified representation of a single trade execution."""
    id: str
    order_id: str
    eid: str
    price: float
    amount: float
    side: str
    timestamp: int
    fee: float
    fee_currency: str
    info: Optional[Dict] = None

@dataclass(frozen=True)
class Order:
    """Unified representation of an order."""
    id: str
    eid: str
    timestamp: int
    type: str
    side: str
    status: str
    amount: float
    filled: float
    price: Optional[float]
    average_price: Optional[float] = None
    trades: List[Trade] = field(default_factory=list)
    info: Optional[Dict] = None

@dataclass(frozen=True)
class Market:
    """
    Represents all metadata and rules for a single trading instrument on an exchange.
    This is the backbone of the framework's standardization.
    """
    # --- Required fields (no default value) ---
    id: str
    symbol: str
    eid: str
    instrument: Instrument
    active: bool
    contract: bool
    info: Dict  # <--- FIX: Moved up

    # --- Optional fields (with default values) ---
    precision: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)
    contract_size: Optional[float] = 1.0