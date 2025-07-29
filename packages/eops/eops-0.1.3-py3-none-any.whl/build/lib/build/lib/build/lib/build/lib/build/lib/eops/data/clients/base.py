# eops/data/clients/base.py
from abc import ABC, abstractmethod
from typing import List

class BaseDataClient(ABC):
    """
    Abstract Base Class for exchange data clients.
    Defines the interface for fetching OHLCV data.
    """
    
    @abstractmethod
    def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        since: int, 
        limit: int
    ) -> List[list]:
        """
        Fetch OHLCV (Kline) data.

        Args:
            symbol (str): Unified symbol format, e.g., 'BTC/USDT'.
            timeframe (str): Unified timeframe, e.g., '1h', '1d'.
            since (int): The starting timestamp in milliseconds.
            limit (int): The number of candles to fetch.

        Returns:
            A list of lists, where each inner list is [timestamp, open, high, low, close, volume].
            Returns an empty list if no data is available.
        """
        pass