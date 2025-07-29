# eops/data/clients/binance.py
import requests
from typing import List
from .base import BaseDataClient
from eops.utils.logger import log

class BinanceClient(BaseDataClient):
    """Data client for Binance."""
    
    BASE_URL = "https://api.binance.com"

    def fetch_ohlcv(self, symbol: str, timeframe: str, since: int, limit: int) -> List[list]:
        api_symbol = symbol.replace('/', '')
        endpoint = f"{self.BASE_URL}/api/v3/klines"
        
        params = {
            "symbol": api_symbol,
            "interval": timeframe,
            "startTime": since,
            "limit": limit
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            
            # Convert string data to numeric types
            # Binance format: [open_time, open, high, low, close, volume, ...]
            ohlcv = []
            for d in data:
                ohlcv.append([
                    int(d[0]),      # timestamp
                    float(d[1]),    # open
                    float(d[2]),    # high
                    float(d[3]),    # low
                    float(d[4]),    # close
                    float(d[5])     # volume
                ])
            return ohlcv
            
        except requests.exceptions.RequestException as e:
            log.error(f"Binance API request failed: {e}")
            return []
        except Exception as e:
            log.error(f"An error occurred while processing Binance data: {e}")
            return []