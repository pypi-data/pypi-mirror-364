# examples/strategies/ema_cross.py 
import asyncio
from typing import List, Set, Dict, Any
from dataclasses import asdict
from collections import deque
import pandas as pd

from eops.core.strategy import BaseStrategy
from eops.core.handler import BaseUpdater, BaseDecider, BaseExecutor, BaseEventHandler
from eops.core.event import Event, EventType
from eops.core.backtest.updater import BacktestUpdater
from eops.clients import BaseClient
from eops.models import common

class LiveKlineUpdater(BaseUpdater):
    async def run(self):
        self.log.warning("LiveKlineUpdater is a placeholder and does not stream real data yet.")
        await asyncio.sleep(1)

class IndicatorHandler(BaseEventHandler):
    @property
    def subscribed_events(self) -> Set[EventType]: return {EventType.MARKET}

    def __init__(self, strategy: BaseStrategy):
        super().__init__(strategy)
        self.short_period = self.strategy.params.get('short_ema', 10)
        self.long_period = self.strategy.params.get('long_ema', 20)
        self.history_close = deque(maxlen=self.long_period * 2 + 50)

    async def process(self, event: Event):
        self.history_close.append(event.data['close'])
        if len(self.history_close) < self.long_period: return

        close_series = pd.Series(list(self.history_close))
        ema_short = close_series.ewm(span=self.short_period, adjust=False).mean().iloc[-1]
        ema_long = close_series.ewm(span=self.long_period, adjust=False).mean().iloc[-1]
        
        self.strategy.shared_state['ema_short'] = ema_short
        self.strategy.shared_state['ema_long'] = ema_long

class PositionManager(BaseEventHandler):
    @property
    def subscribed_events(self) -> Set[EventType]: return {EventType.FILL}

    def __init__(self, strategy: BaseStrategy):
        super().__init__(strategy)
        self.instrument_id = self.strategy.params['instrument_id']
        self.strategy.shared_state['position_amount'] = 0.0

    async def process(self, event: Event):
        fill_data: common.Order = event.data 
        if fill_data.eid != self.strategy.params['instrument_id']: return
        
        current_pos = self.strategy.shared_state['position_amount']
        
        change = fill_data.filled
        if fill_data.side == common.OrderSide.SELL:
            change = -change

        self.strategy.shared_state['position_amount'] += change
        
        self.log.info(f"Position updated. Old: {current_pos:.4f}, New: {self.strategy.shared_state['position_amount']:.4f}, Fill: {fill_data.side.value} {fill_data.filled}")

class CrossDecider(BaseDecider):
    @property
    def subscribed_events(self) -> Set[EventType]: return {EventType.MARKET}

    def __init__(self, strategy: BaseStrategy):
        super().__init__(strategy)
        # Initialize prev_ema values in the shared state
        self.strategy.shared_state['prev_ema_short'] = 0.0
        self.strategy.shared_state['prev_ema_long'] = 0.0

    async def process(self, event: Event):
        state = self.strategy.shared_state
        params = self.strategy.params
        ema_short, ema_long = state.get('ema_short'), state.get('ema_long')
        position_amount = state.get('position_amount', 0.0)
        
        if ema_short is None or ema_long is None: return
        
        # Retrieve previous EMA values
        prev_ema_short = state.get('prev_ema_short', ema_short)
        prev_ema_long = state.get('prev_ema_long', ema_long)

        # Check for crossover conditions
        is_golden_cross = ema_short > ema_long
        was_dead_cross = prev_ema_short <= prev_ema_long
        
        is_dead_cross = ema_short < ema_long
        was_golden_cross = prev_ema_short >= prev_ema_long
        
        # Log every tick for debugging
        # self.log.info(
        #     f"Tick @ {event.data['time']:%Y-%m-%d %H:%M} | "
        #     f"EMA_S: {ema_short:.2f}, EMA_L: {ema_long:.2f} | "
        #     f"Prev_S: {prev_ema_short:.2f}, Prev_L: {prev_ema_long:.2f} | "
        #     f"Position: {position_amount}"
        # )

        # Update previous EMA values for the next tick
        state['prev_ema_short'] = ema_short
        state['prev_ema_long'] = ema_long
        
        instrument_id = params['instrument_id']
        order_amount = params['order_amount']
        
        if is_golden_cross and was_dead_cross and position_amount == 0:
            self.log.info(f"Golden Cross DETECTED @ {event.data['time']:%Y-%m-%d %H:%M}. GO LONG.")
            self.put_nowait(Event(EventType.ORDER, data={
                'instrument_id': instrument_id, 'side': common.OrderSide.BUY, 
                'type': common.OrderType.MARKET, 'amount': order_amount
            }))
        elif is_dead_cross and was_golden_cross and position_amount > 0:
            self.log.info(f"Dead Cross DETECTED @ {event.data['time']:%H:%M}. CLOSE LONG.")
            self.put_nowait(Event(EventType.ORDER, data={
                'instrument_id': instrument_id, 'side': common.OrderSide.SELL, 
                'type': common.OrderType.MARKET, 'amount': position_amount
            }))

class GenericExecutor(BaseExecutor):
    @property
    def subscribed_events(self) -> Set[EventType]: return {EventType.ORDER}

    async def process(self, event: Event):
        order_data = event.data
        client: BaseClient = self.strategy.context['client']
        
        try:
            self.log.info(f"Executor received order: {order_data}")
            trade_result = await client.create_order(
                instrument_id=order_data['instrument_id'], 
                type=order_data['type'],
                side=order_data['side'], 
                amount=order_data['amount']
            )
            self.put_nowait(Event(event_type=EventType.FILL, data=trade_result))
            self.log.info(f"Order executed, fill event dispatched for order {trade_result.id}")
        except Exception as e:
            self.log.error(f"Order execution failed for {order_data['instrument_id']}: {e}", exc_info=True)


class EmaCrossStrategy(BaseStrategy):
    @staticmethod
    def describe_params() -> List[Dict[str, Any]]:
        return [
            {'name': 'instrument_id', 'type': 'str', 'default': 'BTC/USDT', 'label': 'Instrument ID'},
            {'name': 'timeframe', 'type': 'str', 'default': '1h', 'label': 'Timeframe'},
            {'name': 'short_ema', 'type': 'int', 'default': 10, 'label': 'Short EMA Period'},
            {'name': 'long_ema', 'type': 'int', 'default': 20, 'label': 'Long EMA Period'},
            {'name': 'order_amount', 'type': 'float', 'default': 0.1, 'label': 'Order Amount'}
        ]

    def _create_updaters(self) -> List[BaseUpdater]:
        if self.mode == 'backtest':
            return [BacktestUpdater(self, self.context['backtest_data_path'])]
        return [LiveKlineUpdater(self)]

    def _create_event_handlers(self) -> List[BaseEventHandler]:
        return [IndicatorHandler(self), PositionManager(self)]

    def _create_deciders(self) -> List[BaseDecider]:
        return [CrossDecider(self)]

    def _create_executors(self) -> List[BaseExecutor]:
        return [GenericExecutor(self)]

SmaCrossStrategy = EmaCrossStrategy