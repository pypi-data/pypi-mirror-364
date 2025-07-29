# examples/strategies/sma_cross_strategy.py
import pandas as pd
from typing import Dict, Any, List, Set

# --- Import a common base classes for the pipeline ---
from eops.core.strategy import BaseStrategy
from eops.core.handler import (
    BaseUpdater, BaseEventHandler, BaseDecider, BaseExecutor
)
from eops.core.event import Event, EventType, event_bus

# --- Import backtesting-specific components ---
# In a real-world scenario, you might have different files for live components
from eops.core.backtest.updater import BacktestUpdater
from eops.core.backtest.executor import BacktestExecutor

# ====================================================================
#  UADE Pipeline Component Implementations for this Strategy
# ====================================================================

# -------------------- ANALYZE (EventHandler) --------------------
class SmaIndicatorHandler(BaseEventHandler):
    """
    Analyzes market data to calculate SMA indicators.
    It consumes MARKET events and stores results in the strategy's shared state.
    """
    def __init__(self, strategy: 'BaseStrategy'):
        super().__init__(strategy)
        self.warmup_period = self.strategy.params.get("long_window", 30)

    @property
    def subscribed_events(self) -> Set[EventType]:
        return {EventType.MARKET}

    def process(self, event: Event):
        symbol = self.strategy.params.get("symbol")
        klines = self.strategy.context['exchange'].get_klines(
            symbol=symbol,
            timeframe='1h',
            limit=self.warmup_period + 2
        )

        if len(klines) < self.warmup_period + 2:
            return

        df = pd.DataFrame(klines)
        short_sma = df['close'].rolling(window=self.strategy.params.get("short_window")).mean()
        long_sma = df['close'].rolling(window=self.strategy.params.get("long_window")).mean()

        # Write analysis results to the shared "blackboard"
        self.strategy.shared_state['short_sma'] = short_sma.iloc[-1]
        self.strategy.shared_state['prev_short_sma'] = short_sma.iloc[-2]
        self.strategy.shared_state['long_sma'] = long_sma.iloc[-1]
        self.strategy.shared_state['prev_long_sma'] = long_sma.iloc[-2]
        self.log.debug(f"Indicators updated: short={short_sma.iloc[-1]:.2f}, long={long_sma.iloc[-1]:.2f}")


# -------------------- DECIDE (Decider) --------------------
class SmaCrossoverDecider(BaseDecider):
    """
    Makes trading decisions based on SMA crossover signals.
    It consumes MARKET events (to trigger a check) and produces ORDER events.
    """
    @property
    def subscribed_events(self) -> Set[EventType]:
        return {EventType.MARKET}

    def process(self, event: Event):
        # Read analysis results from the shared "blackboard"
        short_sma = self.strategy.shared_state.get('short_sma')
        if short_sma is None:
            return # Indicators are not ready yet

        prev_short_sma = self.strategy.shared_state['prev_short_sma']
        long_sma = self.strategy.shared_state['long_sma']
        prev_long_sma = self.strategy.shared_state['prev_long_sma']

        position = self.strategy.context['exchange'].get_position(self.strategy.params.get("symbol"))
        position_size = position.get('long', 0.0)

        buy_signal = prev_short_sma <= prev_long_sma and short_sma > long_sma
        sell_signal = prev_short_sma >= prev_long_sma and short_sma < long_sma

        if buy_signal and position_size == 0:
            self.log.info(f"BUY SIGNAL detected. Emitting ORDER event.")
            order_event = Event(event_type=EventType.ORDER, data={
                'symbol': self.strategy.params.get("symbol"),
                'side': 'buy',
                'amount': self.strategy.params.get("trade_amount"),
                'order_type': 'market'
            })
            event_bus.put(order_event)

        elif sell_signal and position_size > 0:
            self.log.info(f"SELL SIGNAL detected. Emitting ORDER event.")
            order_event = Event(event_type=EventType.ORDER, data={
                'symbol': self.strategy.params.get("symbol"),
                'side': 'sell',
                'amount': position_size,
                'order_type': 'market'
            })
            event_bus.put(order_event)


# ====================================================================
#  The Main Strategy Class that assembles the pipeline
# ====================================================================

class SmaCrossStrategy(BaseStrategy):
    """
    A full strategy defined by its UADE pipeline components.
    This class is responsible for constructing the pipeline.
    """
    # -------------------- UPDATE (Updater) --------------------
    def _create_updaters(self) -> List[BaseUpdater]:
        """Constructs the data source for the strategy."""
        # For a backtest, we use the BacktestUpdater and pass it the data path
        # from the strategy's context, which was put there by the BacktestEngine.
        data_path = self.context.get("backtest_data_path")
        return [BacktestUpdater(self, data_path=data_path)]

    # -------------------- ANALYZE (EventHandler) --------------------
    def _create_event_handlers(self) -> List[BaseEventHandler]:
        """Constructs the data analyzers for the strategy."""
        return [SmaIndicatorHandler(self)]

    # -------------------- DECIDE (Decider) --------------------
    def _create_deciders(self) -> List[BaseDecider]:
        """Constructs the decision-making logic for the strategy."""
        return [SmaCrossoverDecider(self)]

    # -------------------- EXECUTE (Executor) --------------------
    def _create_executors(self) -> List[BaseExecutor]:
        """Constructs the order executors for the strategy."""
        # For a backtest, we use the BacktestExecutor.
        return [BacktestExecutor(self)]