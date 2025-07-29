# eops/models/rest/account.py
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass(frozen=True)
class Balance:
    asset: str
    total: float
    available: float

@dataclass(frozen=True)
class Position:
    eid: str          # Unified Instrument ID
    symbol: str       # Exchange-specific symbol
    amount: float
    side: str
    entry_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    leverage: Optional[float] = None
    info: Optional[Dict] = None