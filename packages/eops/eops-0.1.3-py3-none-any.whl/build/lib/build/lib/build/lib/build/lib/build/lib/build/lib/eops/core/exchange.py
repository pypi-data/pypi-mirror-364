# eops/core/exchange.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseExchange(ABC):
    """
    Abstract Base Class for all exchange implementations.
    The user must implement a class that inherits from this one.
    eops engines will only interact with objects of this type.
    """

    def __init__(self, params: Dict[str, Any]):
        """
        Initialize the exchange connection.
        'params' will be passed from the configuration file.
        e.g., {'api_key': '...', 'secret_key': '...'}
        """
        self.params = params
        self.connect()

    @abstractmethod
    def connect(self):
        """
        Implement the logic to connect to the exchange API.
        This is called during initialization.
        """
        pass

    @abstractmethod
    def get_klines(self, symbol: str, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch Kline/OHLCV data.
        Should return a list of dictionaries, e.g.:
        [{'time': 1672531200000, 'open': 16500, 'high': 16550, 'low': 16480, 'close': 16520, 'volume': 100}, ...]
        """
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> Dict[str, float]:
        """
        Fetch current position for a symbol.
        Should return a dictionary, e.g.:
        {'long': 1.5, 'short': 0.0}
        """
        pass

    @abstractmethod
    def get_balance(self) -> Dict[str, float]:
        """
        Fetch account balance.
        Should return a dictionary, e.g.:
        {'total': 10000.0, 'available': 8000.0}
        """
        pass
    
    @abstractmethod
    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """
        Create a market order.
        
        Args:
            symbol (str): The trading symbol, e.g., 'BCH/USDT'.
            side (str): 'buy' or 'sell'.
            amount (float): The quantity to trade.

        Returns:
            A dictionary representing the order result, e.g.:
            {'id': '12345', 'status': 'filled', 'price': 350.5, 'amount': 0.1}
        """
        pass