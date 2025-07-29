# eops/data/clients/okx.py (支持时间区间的最终版)

import requests
from typing import List, Optional
from .base import BaseDataClient
from eops.utils.logger import log

class OkxClient(BaseDataClient):
    """Data client for OKX."""
    BASE_URL = "https://www.okx.com"
    TIMEFRAME_MAP = {
        '1m': '1m', '3m': '3m', '5m': '5m', '15m': '15m', '30m': '30m',
        '1h': '1H', '2h': '2H', '4h': '4H', '1d': '1Dutc'
    }

    def _convert_timeframe_to_ms(self, timeframe: str) -> int:
        """Converts timeframe string to milliseconds."""
        multipliers = {'m': 60, 'h': 3600, 'd': 86400}
        unit = timeframe[-1].lower()
        value = int(timeframe[:-1])
        return value * multipliers[unit] * 1000

    def fetch_ohlcv(
        self, 
        symbol: str, 
        timeframe: str, 
        since: int, 
        limit: int,
        # 新增的参数，用于精确的区间请求
        before_ts: Optional[int] = None 
    ) -> List[list]:
        """
        Fetches OHLCV data. For OKX, this can use 'after' (since) and 'before' for precise ranges.
        """
        api_symbol = symbol.replace('/', '-')
        api_timeframe = self.TIMEFRAME_MAP.get(timeframe)
        if not api_timeframe:
            raise ValueError(f"Timeframe '{timeframe}' not supported by OKX client. Supported: {list(self.TIMEFRAME_MAP.keys())}")

        endpoint = f"{self.BASE_URL}/api/v5/market/history-candles"
        
        params = {
            "instId": api_symbol,
            "bar": api_timeframe,
            "limit": str(limit) # OKX limit is 300
        }
        # OKX API: after and before are mutually exclusive, but we can use them for our logic.
        # The downloader will call this function with either `since` or `before`.
        # For our new strategy, we will use both to define a window.
        if before_ts:
            params["before"] = str(before_ts)
        # `since` is mapped to `after`
        params["after"] = str(since)

        try:
            req = requests.Request('GET', endpoint, params=params)
            prepared = req.prepare()
            log.debug(f"OKX Request URL: {prepared.url}")
            
            with requests.Session() as s:
                response = s.send(prepared, timeout=10)

            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get("code") != "0":
                log.error(f"OKX API Error: {response_data.get('msg')} (Code: {response_data.get('code')})")
                return []

            data = response_data.get("data", [])
            # Data is descending. Reverse it to be ascending (chrono).
            data.reverse()
            
            ohlcv = [[int(d[0]), float(d[1]), float(d[2]), float(d[3]), float(d[4]), float(d[5])] for d in data]
            return ohlcv
            
        except requests.exceptions.RequestException as e:
            log.error(f"OKX API request failed: {e}")
            return []
        except Exception as e:
            log.error(f"An error occurred while processing OKX data: {e}", exc_info=True)
            return []