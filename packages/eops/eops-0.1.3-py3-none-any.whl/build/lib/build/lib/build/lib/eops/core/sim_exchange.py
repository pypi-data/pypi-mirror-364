# eops/core/sim_exchange.py
from typing import Dict, Any, List
import pandas as pd
from .exchange import BaseExchange
from .portfolio import Portfolio

class SimulatedExchange(BaseExchange):
    """
    A simulated exchange for backtesting. It uses historical data to fill orders.
    """
    def __init__(self, data: pd.DataFrame, portfolio: Portfolio, fee_rate: float):
        self.data = data
        self.portfolio = portfolio
        self.fee_rate = fee_rate
        self._current_index = -1
        self._current_tick: pd.Series = None # Explicitly type hint as a Series

    def connect(self):
        pass

    def tick(self, index: int):
        """Advances the simulation to the next data point."""
        if index < 0 or index >= len(self.data):
            raise IndexError("Tick index is out of bounds for the provided data.")
        self._current_index = index
        self._current_tick = self.data.iloc[self._current_index]

    def _get_current_price(self, symbol: str) -> float:
        if self._current_tick is None:
            raise ValueError("Simulation has not started. Call tick() first.")
        # Assumes the 'close' price is what we trade on.
        return self._current_tick['close']
    
    def get_klines(self, symbol: str, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        if self._current_index < 0:
            return []
        
        start_index = max(0, self._current_index - limit + 1)
        end_index = self._current_index + 1
        
        # When converting to dict, we need to bring the index back as a 'time' column
        kline_df = self.data.iloc[start_index:end_index]
        kline_df = kline_df.reset_index()
        # Ensure column name is 'time'
        kline_df = kline_df.rename(columns={'index': 'time'}) 
        return kline_df.to_dict('records')

    def get_position(self, symbol: str) -> Dict[str, float]:
        amount = self.portfolio.get_position_value(symbol)
        return {'long': amount, 'short': 0.0}

    def get_balance(self) -> Dict[str, float]:
        last_equity = self.portfolio.equity_curve[-1]['equity'] if self.portfolio.equity_curve else self.portfolio.initial_cash
        return {'total': last_equity, 'available': self.portfolio.cash}

    def create_market_order(self, symbol: str, side: str, amount: float) -> Dict[str, Any]:
        """Simulates the execution of a market order."""
        if self._current_tick is None:
            raise ValueError("Cannot create order, simulation tick has not been set.")

        price = self._get_current_price(symbol)
        cost = amount * price
        fee = cost * self.fee_rate
        
        if side == 'buy':
            if self.portfolio.cash < cost + fee:
                raise ValueError(f"Insufficient funds to buy {amount} {symbol}.")
        elif side == 'sell':
            if self.portfolio.get_position_value(symbol) < amount:
                raise ValueError(f"Insufficient position to sell {amount} {symbol}.")

        # --- HERE IS THE FIX ---
        # The timestamp is the 'name' of the Series, as it was the DataFrame's index.
        timestamp = self._current_tick.name
        # --- END OF FIX ---

        self.portfolio.record_trade(
            timestamp=timestamp,
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            fee=fee
        )
        
        return {
            'id': f'sim_{len(self.portfolio.trades)}',
            'status': 'filled',
            'price': price,
            'amount': amount,
            'fee': fee
        }