# eops/clients/backtest.py
import pandas as pd
import uuid
from typing import Dict, Any, Optional, List
from logging import Logger

from .base import BaseClient
from .errors import InsufficientFunds, InvalidOrder, OrderNotFound, NotSupported
from eops.models import common
from eops.models.rest import account, market, order
from eops.instruments import Instrument, parse_eid
from eops.utils.logger import log as framework_log

# --- Portfolio: The Heart of the Backtest Simulation ---

class Portfolio:
    """
    Manages the state of a simulated account during a backtest, including cash,
    positions, equity, and order/trade history.
    """
    def __init__(self, initial_cash: float = 10000.0, fee_rate: float = 0.001, log: Logger = None):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.fee_rate = fee_rate
        self.positions: Dict[str, account.Position] = {} # eid -> Position object
        self.trades: List[order.Trade] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.log = log or framework_log

    def get_balance(self, asset: str) -> account.Balance:
        if asset.upper() == 'USDT':
            return account.Balance(asset='USDT', total=self.cash, available=self.cash)
        
        total_amount = 0.0
        for pos in self.positions.values():
            instrument = parse_eid(pos.eid).instrument
            if instrument.base_symbol == asset:
                total_amount += pos.amount
        return account.Balance(asset=asset, total=total_amount, available=total_amount)

    def update_equity(self, timestamp: Any, current_prices: Dict[str, float]):
        market_value = 0.0
        for eid, pos in self.positions.items():
            if pos.amount != 0:
                price = current_prices.get(eid, pos.entry_price)
                market_value += pos.amount * price
        
        total_equity = self.cash + market_value
        self.equity_curve.append({"timestamp": timestamp, "equity": total_equity})

    def execute_market_order(self, market_info: market.Market, side: common.OrderSide, amount: float, price: float, timestamp: int) -> order.Order:
        """Simulates the execution of a market order."""
        instrument = market_info.instrument
        cost = amount * price
        fee = cost * self.fee_rate

        # --- ADDED LOGGING & LOGIC FIX ---
        self.log.info(f"Executing order check: Side={side}, Amount={amount}, Price={price:.2f}, Cost={cost:.2f}, Fee={fee:.2f}, Cash={self.cash:.2f}")

        if side == common.OrderSide.BUY and self.cash < cost + fee:
            raise InsufficientFunds(f"Not enough cash ({self.cash:.2f}) to buy {amount} {instrument.base_symbol} (cost: {cost+fee:.2f}).")
        
        current_pos = self.positions.get(market_info.eid)
        current_amount = current_pos.amount if current_pos else 0.0
        
        if side == common.OrderSide.SELL and current_amount < amount:
            raise InsufficientFunds(f"Not enough position ({current_amount}) to sell {amount} {instrument.base_symbol}.")

        # --- MOVED TRADE CREATION TO AFTER CHECKS ---
        # All checks passed, now we can execute and record the trade.
        order_id = f"sim-{uuid.uuid4().hex[:8]}"
        trade_id = f"trade-{uuid.uuid4().hex[:8]}"
        new_trade = order.Trade(
            id=trade_id, order_id=order_id, eid=market_info.eid, symbol=market_info.symbol,
            price=price, amount=amount, side=side, timestamp=timestamp, fee_cost=fee, fee_currency=instrument.quote_currency
        )
        self.trades.append(new_trade)

        if side == common.OrderSide.BUY:
            self.cash -= (cost + fee)
        else: # SELL
            self.cash += (cost - fee)
            
        new_amount = current_amount + amount if side == common.OrderSide.BUY else current_amount - amount
        
        if new_amount == 0:
            self.positions.pop(market_info.eid, None)
        else:
            if side == common.OrderSide.BUY:
                new_entry_price = ((current_pos.entry_price * current_amount) + (price * amount)) / new_amount if current_pos else price
            else:
                new_entry_price = current_pos.entry_price # Entry price doesn't change on partial or full close
            
            self.positions[market_info.eid] = account.Position(
                eid=market_info.eid, symbol=market_info.symbol, amount=new_amount, 
                side='long' if new_amount > 0 else 'short', entry_price=new_entry_price
            )

        self.log.info(f"TRADE EXECUTED: {side.name} {amount} {market_info.symbol} @ {price:.2f} | New Cash: {self.cash:.2f}")
        
        return order.Order(
            id=order_id, eid=market_info.eid, symbol=market_info.symbol, timestamp=timestamp,
            type=common.OrderType.MARKET, side=side, status='filled', amount=amount, filled=amount,
            price=price, average_price=price, cost=(amount * price), trades=[new_trade]
        )

# --- BacktestClient Implementation ---

class BacktestClient(BaseClient):
    def __init__(self, data_path: str, instrument_id: str, initial_cash: float = 10000.0, fee_rate: float = 0.001, **kwargs):
        super().__init__(**kwargs)
        self.instrument_id = instrument_id
        
        try:
            self.data: pd.DataFrame = pd.read_csv(data_path, parse_dates=['time'], index_col='time')
        except FileNotFoundError:
            raise FileNotFoundError(f"Backtest data file not found at: {data_path}")
            
        self.portfolio = Portfolio(initial_cash=initial_cash, fee_rate=fee_rate)
        self._current_tick: Optional[pd.Series] = None
        self._current_index = -1
        
        try:
            instrument = parse_eid(self.instrument_id)
            symbol = f"{instrument.base_symbol}/{instrument.quote_currency}"
        except ValueError:
            parts = self.instrument_id.split('/')
            instrument = Instrument(asset_class="CRYPTO", base_symbol=parts[0], quote_currency=parts[1], product_type="SPOT")
            symbol = self.instrument_id
        
        eid = instrument.to_eid()
        market_obj = market.Market(
            id=symbol, symbol=symbol, eid=eid, instrument=instrument,
            active=True, is_spot=True, is_future=False, info={}
        )
        
        self.markets[eid] = market_obj
        self.markets_by_id[symbol] = market_obj
        self._markets_loaded.set()

        framework_log.info(f"BacktestClient initialized for '{self.instrument_id}' with data from {self.data.index.min()} to {self.data.index.max()}")

    def tick(self, timestamp: pd.Timestamp):
        try:
            loc = self.data.index.asof(timestamp)
            if loc is not pd.NaT:
                idx = self.data.index.get_loc(loc)
                if idx > self._current_index:
                    self._current_index = idx
                    self._current_tick = self.data.iloc[self._current_index]
                    market_info = list(self.markets.values())[0]
                    self.portfolio.update_equity(
                        self._current_tick.name, 
                        {market_info.eid: self._current_tick['close']}
                    )
        except KeyError:
            pass

    async def fetch_markets(self) -> List[market.Market]:
        return list(self.markets.values())

    async def fetch_balances(self) -> List[account.Balance]:
        balances = [self.portfolio.get_balance('USDT')]
        for pos in self.portfolio.positions.values():
            base, _ = pos.symbol.split('/')
            balances.append(self.portfolio.get_balance(base))
        return balances

    async def fetch_positions(self, instrument_id: Optional[str] = None) -> List[account.Position]:
        market_info = await self._resolve_market(instrument_id or self.instrument_id)
        if instrument_id:
            return [self.portfolio.positions.get(market_info.eid)] if market_info.eid in self.portfolio.positions else []
        return list(self.portfolio.positions.values())

    async def fetch_klines(self, instrument_id: str, timeframe: str, since: Optional[int] = None, limit: Optional[int] = 100) -> List[market.Kline]:
        await self._resolve_market(instrument_id)
        if self._current_index < 0: return []
        
        start_index = max(0, self._current_index - limit + 1)
        end_index = self._current_index + 1
        kline_df = self.data.iloc[start_index:end_index]
        return [market.Kline(**row.to_dict(), timestamp=row.name.value // 1_000_000) for _, row in kline_df.iterrows()]

    async def fetch_ticker(self, instrument_id: str) -> market.Ticker:
        market_info = await self._resolve_market(instrument_id)
        if self._current_tick is None: raise ValueError("Backtest not ticked.")
        
        return market.Ticker(
            eid=market_info.eid, symbol=market_info.symbol,
            timestamp=self._current_tick.name.value // 1_000_000,
            last=self._current_tick['close']
        )

    async def create_order(self, instrument_id: str, type: common.OrderType, side: common.OrderSide, amount: float, price: Optional[float] = None) -> order.Order:
        market_info = await self._resolve_market(instrument_id)
        if self._current_tick is None:
            raise InvalidOrder("Cannot create order: backtest has not been ticked with data.")
        if type != common.OrderType.MARKET:
            raise NotSupported("BacktestClient currently only supports Market orders.")
        
        exec_price = self._current_tick['close']
        timestamp_ms = self._current_tick.name.value // 1_000_000
        return self.portfolio.execute_market_order(market_info, side, amount, exec_price, timestamp_ms)

    async def cancel_order(self, order_id: str, instrument_id: Optional[str] = None) -> order.Order:
        raise OrderNotFound(f"Cannot cancel order '{order_id}': all orders are filled instantly.")

    async def fetch_order(self, order_id: str, instrument_id: Optional[str] = None) -> order.Order:
        raise NotSupported("fetch_order is not implemented in this backtester.")

    async def fetch_open_orders(self, instrument_id: Optional[str] = None) -> List[order.Order]:
        return []
        
    async def fetch_my_trades(self, instrument_id: Optional[str] = None, since: Optional[int] = None, limit: Optional[int] = None) -> List[order.Trade]:
        return list(self.portfolio.trades)