# eops/models/rest/market.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from eops.instruments import Instrument # Import Instrument

@dataclass(frozen=True)
class Kline:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: Optional[float] = None

@dataclass(frozen=True)
class Ticker:
    eid: str
    symbol: str
    timestamp: int
    last: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    info: Optional[Dict] = None

@dataclass(frozen=True)
class Market:
    id: str
    symbol: str
    eid: str
    instrument: Instrument # Store the parsed Instrument object
    active: bool
    is_spot: bool
    is_future: bool
    info: Dict
    precision: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)