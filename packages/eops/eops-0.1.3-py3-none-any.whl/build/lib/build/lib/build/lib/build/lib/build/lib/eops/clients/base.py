# eops/clients/base.py
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from eops.models.rest import account, market, order
from eops.models.common import OrderSide, OrderType
from eops.instruments import Instrument, parse_eid
from .errors import NotSupported, ExchangeError
from eops.utils.logger import log

class BaseClient(ABC):
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        **kwargs
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.log = log

        self.markets: Dict[str, market.Market] = {} # eid -> Market
        self.markets_by_id: Dict[str, market.Market] = {} # native_id -> Market
        
        self._markets_loaded = asyncio.Event()

    async def load_markets(self, force_reload: bool = False):
        """
        Loads and caches market data. This must be called before most other methods.
        """
        if self._markets_loaded.is_set() and not force_reload:
            return
        
        self.log.info(f"Loading markets for {self.__class__.__name__}...")
        try:
            markets_list = await self.fetch_markets()
            self.markets = {m.eid: m for m in markets_list}
            self.markets_by_id = {m.id: m for m in markets_list}
            self._markets_loaded.set()
            self.log.info(f"Successfully loaded {len(self.markets)} markets.")
        except Exception as e:
            self.log.error(f"Failed to load markets: {e}", exc_info=True)
            self._markets_loaded.clear()
            raise ExchangeError(f"Failed to load markets: {e}") from e

    async def _resolve_market(self, instrument_id: str) -> market.Market:
        """
        Resolves an instrument identifier (EID or native ID) to a market object.
        Loads markets if they haven't been loaded yet.
        """
        if not self._markets_loaded.is_set():
            await self.load_markets()
        
        # Is it an EID?
        if instrument_id in self.markets:
            return self.markets[instrument_id]
        
        # Is it a native ID?
        if instrument_id in self.markets_by_id:
            return self.markets_by_id[instrument_id]
            
        # Try parsing as EID to handle cases with no market, e.g. CRYPTO:BTC@USD_SPOT
        try:
            parsed_instrument = parse_eid(instrument_id)
            # This is a fallback and might not work for all exchanges/methods
            # It's better to use an EID that includes the market.
            # A more robust implementation could search for a matching instrument.
        except ValueError:
            pass # Not a valid EID format

        raise ExchangeError(f"Unknown instrument identifier: '{instrument_id}'. Not found in loaded markets.")

    # --- Abstract Methods for Subclasses to Implement ---
    
    @abstractmethod
    async def fetch_markets(self) -> List[market.Market]:
        """
        Fetches all market data from the exchange and converts it to a list of
        standardized `eops.models.rest.market.Market` objects.
        """
        raise NotSupported()

    # (The rest of the abstract methods are now defined with `instrument_id`)

    async def fetch_balances(self) -> List[account.Balance]:
        raise NotSupported()

    async def fetch_positions(self, instrument_id: Optional[str] = None) -> List[account.Position]:
        raise NotSupported()
        
    async def fetch_klines(
        self, instrument_id: str, timeframe: str, before: Optional[int] = None, after: Optional[int] = None,limit: Optional[int] = 100
    ) -> List[market.Kline]:
        raise NotSupported()
    
    async def fetch_ticker(self, instrument_id: str) -> market.Ticker:
        raise NotSupported()
        
    async def create_order(
        self, instrument_id: str, type: OrderType, side: OrderSide, amount: float, price: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> order.Order:
        raise NotSupported()

    async def cancel_order(self, order_id: str, instrument_id: Optional[str] = None) -> order.Order:
        raise NotSupported()

    async def fetch_order(self, order_id: str, instrument_id: Optional[str] = None) -> order.Order:
        raise NotSupported()

    async def fetch_open_orders(self, instrument_id: Optional[str] = None) -> List[order.Order]:
        raise NotSupported()
        
    async def fetch_my_trades(
        self, instrument_id: Optional[str] = None, since: Optional[int] = None, limit: Optional[int] = None
    ) -> List[order.Trade]:
        raise NotSupported()