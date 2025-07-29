# eops/clients/okx.py
import time
import hmac
import hashlib
import json
import base64
import asyncio
import urllib.parse
from typing import Dict, Any, Optional, List, AsyncIterable
from decimal import Decimal

import websockets

from .base import BaseClient
from eops.models import Kline, Balance, Order, Position, Market, Trade
from eops.instruments import Instrument, parse_eid, InstrumentError

class OkxClient(BaseClient):
    """
    Client for interacting with the OKX exchange.
    Implements the BaseClient interface with EID support.
    """
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None,
                 passphrase: Optional[str] = None, is_demo: bool = False):
        base_url = "https://www.okx.com"
        self.ws_public_url = "wss://ws.okx.com:8443/ws/v5/public"
        self.ws_private_url = "wss://ws.okx.com:8443/ws/v5/private"
        super().__init__(api_key, secret_key, passphrase, base_url=base_url)
        self.is_demo = is_demo
        if is_demo: self.session.headers.update({'x-simulated-trading': '1'})

    # --- Market Loading and EID Implementation ---

    async def fetch_markets(self) -> Dict[str, Market]:
        path = "/api/v5/public/instruments"
        inst_types = ['SPOT', 'SWAP', 'FUTURES', 'OPTION']
        markets = {}
        
        loop = asyncio.get_running_loop()

        for inst_type in inst_types:
            params = {'instType': inst_type}
            
            # --- FIX: Add required parameters for OPTION type ---
            if inst_type == 'OPTION':
                # OKX requires 'uly' or 'instFamily' for options. We'll fetch for
                # major underlyings to get a comprehensive list.
                underlyings = ['BTC-USD', 'ETH-USD']
            else:
                underlyings = [None] # For other types, run loop once

            for uly in underlyings:
                if uly:
                    params['uly'] = uly
                
                response = await loop.run_in_executor(None, self._request, 'GET', path, params)
                
                for raw_market in response.get('data', []):
                    try:
                        if raw_market.get('state') != 'live': continue

                        # Parse instrument and EID
                        inst = self._parse_instrument(raw_market, inst_type)
                        eid = inst.to_eid()

                        # Skip if already processed (can happen with multiple uly calls)
                        if eid in markets: continue

                        # Parse other market details
                        ct_val_str = raw_market.get('ctVal', '1.0')
                        contract_size_val = ct_val_str if ct_val_str else '1.0'
                        
                        market = Market(
                            id=raw_market['instId'], symbol=f"{raw_market.get('baseCcy', '')}/{raw_market.get('quoteCcy', '')}",
                            eid=eid, instrument=inst, active=True,
                            precision={'price': self._get_precision_from_tick_size(raw_market['tickSz']),
                                       'amount': self._get_precision_from_tick_size(raw_market['lotSz'])},
                            limits={'amount': {'min': float(raw_market['minSz'])}},
                            contract=inst_type != 'SPOT', contract_size=Decimal(contract_size_val),
                            info=raw_market
                        )
                        markets[eid] = market
                    except (KeyError, ValueError) as e:
                        self.log.warning(f"Could not parse OKX market {raw_market.get('instId')}: {e}")
        return markets

    def _parse_instrument(self, raw_market: Dict, inst_type: str) -> Instrument:
        base = raw_market['baseCcy']
        quote = raw_market['quoteCcy']
        if not quote and 'ctValCcy' in raw_market:
            quote = raw_market['ctValCcy']

        return Instrument(
            asset_class='CRYPTO', base_symbol=base, market='okx', quote_currency=quote,
            product_type=inst_type if inst_type != 'SWAP' else 'PERP'
        )

    def _get_precision_from_tick_size(self, tick_size: str) -> int:
        d = Decimal(tick_size)
        return -d.as_tuple().exponent if d > 0 else 0

    # --- REST API Implementation (Async) ---

    def _sign_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        method = method.upper()
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S.', time.gmtime()) + f"{time.time_ns() % 1_000_000_000 // 1_000_000:03d}Z"
        body_str = json.dumps(data) if data else ""
        query_str = ""
        if params: query_str = "?" + urllib.parse.urlencode(sorted(params.items()))
        
        message = f"{timestamp}{method}{path}{query_str}{body_str}"
        mac = hmac.new(self.secret_key.encode('utf-8'), message.encode('utf-8'), digestmod='sha256')
        signature = base64.b64encode(mac.digest()).decode('utf-8')

        return {'OK-ACCESS-KEY': self.api_key, 'OK-ACCESS-SIGN': signature,
                'OK-ACCESS-TIMESTAMP': timestamp, 'OK-ACCESS-PASSPHRASE': self.passphrase}

    async def fetch_klines(self, instrument_id: str, timeframe: str, since: int, limit: int) -> List[Kline]:
        market = await self._resolve_instrument(instrument_id)
        path = "/api/v5/market/history-candles"
        tf_map = {'1m':'1m', '1h':'1H', '4h':'4H', '1d':'1Dutc'}
        params = {'instId': market.id, 'bar': tf_map.get(timeframe, timeframe), 'after': since, 'limit': limit}

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self._request, 'GET', path, params)
        raw_klines = response.get('data', [])
        raw_klines.reverse()
        
        return [ Kline(timestamp=int(k[0]), open=float(k[1]), high=float(k[2]),
                      low=float(k[3]), close=float(k[4]), volume=float(k[5]),
                      turnover=float(k[7])) for k in raw_klines ]

    async def fetch_balance(self) -> List[Balance]:
        path = "/api/v5/asset/balances"
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self._request, 'GET', path)
        data = response.get('data', [])[0] if response.get('data') else {'details': []}
        return [ Balance(asset=b['ccy'], total=float(b['bal']), available=float(b['availBal']))
                 for b in data['details'] ]

    async def fetch_positions(self, instrument_id: Optional[str] = None) -> List[Position]:
        market = await self._resolve_instrument(instrument_id) if instrument_id else None
        path = "/api/v5/account/positions"
        params = {'instId': market.id} if market else {'instType': 'SWAP'}

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self._request, 'GET', path, params)
        data = response.get('data', [])
        
        positions = []
        for p in data:
            if float(p['pos']) != 0:
                pos_market = self.markets_by_id.get(p['instId'])
                if not pos_market: continue
                positions.append(Position(
                    eid=pos_market.eid, amount=float(p['pos']), side=p['posSide'],
                    entry_price=float(p['avgPx']), unrealized_pnl=float(p['upl']),
                    leverage=float(p['lever']), info=p
                ))
        return positions

    async def create_order(self, instrument_id: str, type: str, side: str, amount: float, price: Optional[float] = None) -> Order:
        market = await self._resolve_instrument(instrument_id)
        path = "/api/v5/trade/order"
        data = {'instId': market.id, 'tdMode': 'cash', 'side': side,
                'ordType': type, 'sz': str(amount)}
        if type == 'limit':
            if price is None: raise ValueError("Price must be specified for LIMIT orders.")
            data['px'] = str(price)

        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, self._request, 'POST', path, data=data)
        order_data = response.get('data', [])[0]
        
        return Order(
            id=order_data['ordId'], eid=market.eid, type=type, side=side, status='open',
            price=price, amount=amount, filled=0.0,
            timestamp=int(order_data['ts']), info=order_data
        )

    # --- WebSocket API Implementation ---
    
    async def _ws_heartbeat(self, websocket):
        while websocket.open:
            await asyncio.sleep(25)
            await websocket.send("ping")

    async def subscribe_to_klines(self, instrument_id: str, timeframe: str) -> AsyncIterable[Kline]:
        market = await self._resolve_instrument(instrument_id)
        uri = self.ws_public_url
        if self.is_demo: uri += "?brokerId=9999"
        
        tf_map = {'1m':'1m', '1h':'1H', '4h':'4H', '1d':'1Dutc'}
        channel = f"candle{tf_map.get(timeframe, timeframe)}"
        subscribe_payload = {"op": "subscribe", "args": [{"channel": channel, "instId": market.id}]}
        
        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    self.log.info(f"Connected to OKX Kline WebSocket for {market.id}")
                    asyncio.create_task(self._ws_heartbeat(websocket))
                    await websocket.send(json.dumps(subscribe_payload))
                    
                    while True:
                        message = await websocket.recv()
                        if message == "pong": continue
                        data = json.loads(message)
                        if data.get("arg", {}).get("channel") == channel:
                            for k in data.get("data", []):
                                yield Kline(timestamp=int(k[0]), open=float(k[1]), high=float(k[2]),
                                            low=float(k[3]), close=float(k[4]), volume=float(k[5]),
                                            turnover=float(k[7]))
            except Exception as e:
                self.log.error(f"OKX WebSocket error for {instrument_id}: {e}. Reconnecting...", exc_info=True)
                await asyncio.sleep(5)