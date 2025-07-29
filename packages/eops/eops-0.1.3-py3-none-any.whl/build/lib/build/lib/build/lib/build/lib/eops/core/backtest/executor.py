# eops/core/backtest/executor.py
from typing import Set, TYPE_CHECKING

from ..handler.executor import BaseExecutor
from ..event import Event, EventType
from ..sim_exchange import SimulatedExchange

if TYPE_CHECKING:
    from ..strategy import BaseStrategy

class BacktestExecutor(BaseExecutor):
    """
    An executor for backtesting. It subscribes to ORDER events and interacts
    with the SimulatedExchange to execute trades. It then produces FILL events.
    """
    def __init__(self, strategy: 'BaseStrategy'):
        super().__init__(strategy)
        self.exchange: SimulatedExchange = self.strategy.context['exchange']

    @property
    def subscribed_events(self) -> Set[EventType]:
        return {EventType.ORDER}

    def process(self, event: Event):
        """Processes an ORDER event and simulates its execution."""
        order_data = event.data
        self.log.debug(f"BacktestExecutor received ORDER event: {order_data}")

        try:
            trade_result = self.exchange.create_market_order(
                symbol=order_data.get('symbol'),
                side=order_data.get('side'),
                amount=order_data.get('amount')
            )
            
            if trade_result:
                fill_event = Event(event_type=EventType.FILL, data=trade_result)
                self.log.debug(f"Dispatching FILL event: {fill_event}")
                self.event_bus.put(fill_event)

        except ValueError as e:
            self.log.error(f"Order execution failed for {order_data.get('symbol')}: {e}")
        except Exception as e:
            self.log.error(f"An unexpected error occurred during order execution: {e}", exc_info=True)