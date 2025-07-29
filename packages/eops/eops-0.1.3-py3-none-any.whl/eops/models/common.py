# eops/models/common.py
from enum import Enum

class OrderSide(str, Enum):
    BUY = 'buy'
    SELL = 'sell'

class OrderType(str, Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    # Add other common types like STOP_LOSS, TAKE_PROFIT, etc.