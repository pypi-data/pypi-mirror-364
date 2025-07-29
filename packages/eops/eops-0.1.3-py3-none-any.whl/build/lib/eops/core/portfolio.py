# eops/core/portfolio.py
from typing import List, Dict, Any
from logging import Logger

class Portfolio:
    """
    Manages the state of our account during a backtest, including cash,
    positions, and equity.
    """
    def __init__(self, initial_cash: float = 10000.0, log: Logger = None):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, float] = {}
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []
        self.log = log

    def get_position_value(self, symbol: str) -> float:
        """Returns the quantity of a held asset."""
        return self.positions.get(symbol, 0.0)

    def record_trade(self, timestamp: Any, symbol: str, side: str, amount: float, price: float, fee: float):
        """
        Records a trade and updates cash and positions.
        """
        cost = amount * price
        
        if side == 'buy':
            self.cash -= (cost + fee)
            self.positions[symbol] = self.get_position_value(symbol) + amount
        elif side == 'sell':
            self.cash += (cost - fee)
            self.positions[symbol] = self.get_position_value(symbol) - amount
        
        trade_record = {
            "timestamp": timestamp,
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price,
            "fee": fee
        }
        self.trades.append(trade_record)
        if self.log:
            self.log.info(f"TRADE: {side.upper()} {amount} {symbol} @ {price:.2f} | Fee: {fee:.4f} | Cash: {self.cash:.2f}")

    def update_equity(self, timestamp: Any, current_prices: Dict[str, float]):
        """
        Calculates the total value of the portfolio at a point in time.
        """
        market_value = 0.0
        for symbol, quantity in self.positions.items():
            if quantity != 0:
                market_value += quantity * current_prices.get(symbol, 0)
        
        total_equity = self.cash + market_value
        
        self.equity_curve.append({
            "timestamp": timestamp,
            "equity": total_equity
        })