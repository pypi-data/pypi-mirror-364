# eops/clients/binance.py
import time
import hmac
import hashlib
import json
import urllib.parse
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterable, Tuple # <--- 已导入 Tuple
from decimal import Decimal

import websockets

from .base import BaseClient
from eops.models import Kline, Balance, Order, Position, Market, Trade
from eops.instruments import Instrument

class BinanceClient(BaseClient):
    """
    Client for interacting with the Binance exchange (Spot and Futures).
    Implements the BaseClient interface with EID support.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        is_futures: bool = False,
    ):
        self.is_futures = is_futures
        base_url = "https://fapi.binance.com" if is_futures else "https://api.binance.com"
        self.ws_base_url = "wss://fstream.binance.com" if is_futures else "wss://stream.binance.com:9443"
        super().__init__(api_key, secret_key, base_url=base_url)

    # --- Market Loading and EID Implementation ---
    
    async def fetch_markets(self) -> Dict[str, Market]:
        path = "/fapi/v1/exchangeInfo" if self.is_futures else "/api/v3/exchangeInfo"
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self._request, 'GET', path)
        
        markets = {}
        for raw_market in response.get('symbols', []):
            if raw_market.get('status') != 'TRADING':
                continue

            try:
                base_asset = raw_market['baseAsset']
                quote_asset = raw_market['quoteAsset']
                
                product_type = 'PERP' if self.is_futures and raw_market.get('contractType') == 'PERPETUAL' else \
                             'FUTURES' if self.is_futures else 'SPOT'

                instrument = Instrument(
                    asset_class='CRYPTO', base_symbol=base_asset, market='binance',
                    quote_currency=quote_asset, product_type=product_type,
                )
                eid = instrument.to_eid()
                
                precision, limits = self._parse_filters(raw_market.get('filters', []))

                market = Market(
                    id=raw_market['symbol'], symbol=f"{base_asset}/{quote_asset}",
                    eid=eid, instrument=instrument, active=True,
                    precision=precision, limits=limits, contract=self.is_futures,
                    contract_size=Decimal('1.0'), info=raw_market
                )
                markets[eid] = market

            except (KeyError, ValueError) as e:
                self.log.warning(f"Could not parse Binance market {raw_market.get('symbol')}: {e}")
                continue
                
        return markets

    def _parse_filters(self, filters: List[Dict]) -> Tuple[Dict, Dict]: # <--- FIX: 使用了正确的 Tuple[Dict, Dict] 语法
        """Helper to parse Binance's filter structure."""
        precision = {'price': None, 'amount': None}
        limits = {'price': {}, 'amount': {}, 'cost': {}}
        for f in filters:
            ft = f['filterType']
            if ft == 'PRICE_FILTER':
                precision['price'] = self._get_precision_from_tick_size(f['tickSize'])
                limits['price']['min'] = float(f['minPrice'])
                limits['price']['max'] = float(f['maxPrice'])
            elif ft == 'LOT_SIZE':
                precision['amount'] = self._get_precision_from_tick_size(f['stepSize'])
                limits['amount']['min'] = float(f['minQty'])
                limits['amount']['max'] = float(f['maxQty'])
            elif ft == 'MIN_NOTIONAL':
                limits['cost']['min'] = float(f.get('notional') or f.get('minNotional', 0))
        return precision, limits

    def _get_precision_from_tick_size(self, tick_size: str) -> int:
        d = Decimal(tick_size)
        return -d.as_tuple().exponent if d > 0 else 0

    # --- REST API Implementation (Async) ---
    
    def _sign_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        headers = {'X-MBX-APIKEY': self.api_key}
        all_params = (params or {}).copy()
        if data: all_params.update(data)
        
        all_params['timestamp'] = int(time.time() * 1000)
        query_string = urllib.parse.urlencode(all_params)
        
        signature = hmac.new(self.secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        all_params['signature'] = signature

        # Modify the original params dict in-place for _request method
        if params is not None:
            params.clear()
            params.update(all_params)
        else:
            self._temp_params = all_params

        return headers

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Any:
        final_params = (params or {}).copy()
        if hasattr(self, '_temp_params'):
            final_params.update(self._temp_params)
            del self._temp_params

        if data: final_params.update(data)

        if self.api_key:
            self._sign_request(method, path, params=final_params)

        return super()._request(method, path, params=final_params, data=None)

    async def fetch_klines(self, instrument_id: str, timeframe: str, since: int, limit: int) -> List[Kline]:
        market = await self._resolve_instrument(instrument_id)
        path = "/fapi/v1/klines" if self.is_futures else "/api/v3/klines"
        params = {'symbol': market.id, 'interval': timeframe, 'startTime': since, 'limit': limit}
        
        loop = asyncio.get_running_loop()
        raw_klines = await loop.run_in_executor(None, self._request, 'GET', path, params)
        
        return [ Kline(timestamp=int(k[0]), open=float(k[1]), high=float(k[2]),
                      low=float(k[3]), close=float(k[4]), volume=float(k[5]),
                      turnover=float(k[7])) for k in raw_klines ]

    async def fetch_balance(self) -> List[Balance]:
        path = "/fapi/v2/balance" if self.is_futures else "/api/v3/account"
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self._request, 'GET', path)
        
        balances = data if self.is_futures else data.get('balances', [])
        return [
            Balance(asset=b['asset'],
                    total=float(b.get('balance', 0)) + float(b.get('crossUnPnl', 0)) if self.is_futures else float(b['free']) + float(b['locked']),
                    available=float(b.get('availableBalance', 0)) if self.is_futures else float(b['free']))
            for b in balances if (float(b.get('balance', 0)) > 0 or float(b.get('free', 0)) > 0)
        ]

    async def fetch_positions(self, instrument_id: Optional[str] = None) -> List[Position]:
        if not self.is_futures: return []
        market = await self._resolve_instrument(instrument_id) if instrument_id else None
        
        path = "/fapi/v2/positionRisk"
        params = {'symbol': market.id} if market else {}
        
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self._request, 'GET', path, params)
        
        positions = []
        for p in data:
            if float(p['positionAmt']) != 0:
                pos_market = self.markets_by_id.get(p['symbol'])
                if not pos_market: continue
                positions.append(Position(
                    eid=pos_market.eid, amount=float(p['positionAmt']),
                    side='long' if float(p['positionAmt']) > 0 else 'short',
                    entry_price=float(p['entryPrice']), unrealized_pnl=float(p['unRealizedProfit']),
                    leverage=float(p['leverage']), info=p
                ))
        return positions

    async def create_order(self, instrument_id: str, type: str, side: str, amount: float, price: Optional[float] = None) -> Order:
        market = await self._resolve_instrument(instrument_id)
        path = "/fapi/v1/order" if self.is_futures else "/api/v3/order"
        params = {'symbol': market.id, 'side': side.upper(), 'type': type.upper(), 'quantity': amount}
        if type.lower() == 'limit':
            if price is None: raise ValueError("Price must be specified for LIMIT orders.")
            params['price'] = price
            params['timeInForce'] = 'GTC'

        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, self._request, 'POST', path, data=params)

        return Order(
            id=str(data['orderId']), eid=market.eid, type=data['type'].lower(),
            side=data['side'].lower(), status=data['status'].lower(), price=float(data.get('price', 0.0)),
            amount=float(data['origQty']), filled=float(data['executedQty']),
            average_price=float(data.get('avgPrice', 0.0)),
            timestamp=int(data['updateTime']) if self.is_futures else int(data['transactTime']),
            info=data
        )

    # --- WebSocket API Implementation ---

    async def subscribe_to_klines(self, instrument_id: str, timeframe: str) -> AsyncIterable[Kline]:
        market = await self._resolve_instrument(instrument_id)
        stream_name = f"{market.id.lower()}@kline_{timeframe}"
        uri = f"{self.ws_base_url}/ws/{stream_name}"
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.log.info(f"Connected to Binance Kline WebSocket: {stream_name}")
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        kline_data = data.get('k')
                        if kline_data and kline_data['x']:
                            yield Kline(timestamp=int(kline_data['t']), open=float(kline_data['o']),
                                        high=float(kline_data['h']), low=float(kline_data['l']),
                                        close=float(kline_data['c']), volume=float(kline_data['v']),
                                        turnover=float(kline_data['q']))
            except Exception as e:
                self.log.error(f"Binance WebSocket error for {instrument_id}: {e}. Reconnecting...", exc_info=True)
                await asyncio.sleep(5)