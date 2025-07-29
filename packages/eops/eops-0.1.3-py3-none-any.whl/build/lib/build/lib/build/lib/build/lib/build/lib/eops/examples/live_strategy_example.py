# eops/examples/live_strategy_example.py

from typing import List, Set

from eops.core.strategy import BaseStrategy
from eops.core.handler import BaseDecider, BaseExecutor
from eops.core.event import Event, EventType
from eops.updaters import EopsWebsocketUpdater # Import our new live updater

# --- Decider Component ---
class LiveSignalDecider(BaseDecider):
    def __init__(self, strategy):
        super().__init__(strategy)
        self.instrument = self.strategy.params.get("instrument")
        self.last_price = 0

    @property
    def subscribed_events(self) -> Set[EventType]:
        return {EventType.MARKET}

    def process(self, event: Event):
        # In live mode, the MARKET event data comes from the WebSocket.
        # We expect a "Ticker" event payload.
        if event.data.get("instrument_id") != self.instrument:
            return

        current_price = float(event.data.get("price", 0))
        if current_price == 0:
            return
            
        self.log.info(f"Received market price: {current_price}")

        # Simple logic: if price increases, buy. If it decreases, do nothing.
        # This is a terrible strategy, for demonstration only.
        if self.last_price != 0 and current_price > self.last_price:
            self.log.info(f"Price increased from {self.last_price} to {current_price}. Generating BUY signal.")
            
            order_event = Event(EventType.ORDER, data={
                "symbol": self.instrument,
                "side": "buy",
                "amount": float(self.strategy.params.get("order_amount", 0.001))
            })
            self.event_bus.put(order_event)

        self.last_price = current_price

# --- Executor Component ---
class LiveOrderExecutor(BaseExecutor):
    def __init__(self, strategy):
        super().__init__(strategy)
        self.exchange = self.strategy.context.get("exchange")

    @property
    def subscribed_events(self) -> Set[EventType]:
        return {EventType.ORDER}

    def process(self, event: Event):
        order_data = event.data
        try:
            # The LiveExchange will handle the API call
            self.exchange.create_market_order(
                symbol=order_data.get('symbol'),
                side=order_data.get('side'),
                amount=order_data.get('amount')
            )
            # In live mode, we don't create a FILL event here.
            # We wait for the actual fill event to come back via WebSocket.
        except Exception as e:
            self.log.error(f"Failed to place order: {e}")

# --- Strategy Definition ---
class LiveExampleStrategy(BaseStrategy):
    """
    An example strategy configured for live trading.
    """
    def _create_updaters(self) -> List[EopsWebsocketUpdater]:
        # The strategy tells the updater which topics to subscribe to.
        topics = self.params.get("topics_to_subscribe", [])
        return [EopsWebsocketUpdater(self, subscription_topics=topics)]

    def _create_deciders(self) -> List[LiveSignalDecider]:
        return [LiveSignalDecider(self)]

    def _create_executors(self) -> List[LiveOrderExecutor]:
        return [LiveOrderExecutor(self)]