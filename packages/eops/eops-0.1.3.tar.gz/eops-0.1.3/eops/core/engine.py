# eops/core/engine.py
import pandas as pd
import asyncio
import signal
from collections import defaultdict
from typing import Dict, Any, List, Tuple, Optional
from uuid import uuid4
from dataclasses import asdict

from eops.utils.logger import setup_logger
from eops.core.event import Event, EventType, AsyncDeque
from eops.core.strategy import BaseStrategy
from eops.clients import get_client, BaseClient
from eops.clients.backtest import BacktestClient

class Engine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        if 'MODE' not in config:
            raise ValueError("Config must contain a 'MODE' ('live' or 'backtest').")
        self.mode = config['MODE']
        
        self.instance_id = str(uuid4())
        self.log = setup_logger(self.instance_id, log_file=config.get("LOG_FILE"))
        self.event_bus = AsyncDeque()
        self._running = asyncio.Event()
        self.context: Dict[str, Any] = {'mode': self.mode}
        self.client: BaseClient = None
        self.updater_tasks: List[asyncio.Task] = []
        
        strategy_params = {**(self.config.get("STRATEGY_PARAMS", {}))}
        self.strategy: BaseStrategy = self.config["STRATEGY_CLASS"](
            engine=self, context=self.context, params=strategy_params
        )
        self.handler_map: Dict[EventType, List[Any]] = {}

    async def _initialize_client_and_context(self):
        self.log.info(f"Initializing client for '{self.mode}' mode.")
        if self.mode == 'backtest':
            params = self.config.get("BACKTEST_PARAMS", {})
            strategy_params = self.config.get("STRATEGY_PARAMS", {})
            if 'instrument_id' not in strategy_params:
                raise ValueError("'instrument_id' is required in STRATEGY_PARAMS for backtesting.")
            params['instrument_id'] = strategy_params['instrument_id']
            self.client = get_client('backtest', params)
            self.context['backtest_data_path'] = params.get('data_path')
            if isinstance(self.client, BacktestClient):
                 self.context['portfolio'] = self.client.portfolio
        elif self.mode == 'live':
            params = self.config.get("ENGINE_PARAMS", {})
            client_name = params.get('exchange_name')
            if not client_name:
                raise ValueError("'exchange_name' is required for live mode.")
            self.client = get_client(client_name, params)
        else:
            raise ValueError(f"Unsupported mode: '{self.mode}'.")
        self.context['client'] = self.client
        await self.client.load_markets()

    def _create_handler_map(self):
        handler_map = defaultdict(list)
        processors = (self.strategy.event_handlers + 
                      self.strategy.deciders + 
                      self.strategy.executors)
        for p in processors:
            for et in p.subscribed_events:
                handler_map[et].append(p)
        self.handler_map = handler_map

    async def run(self) -> Optional[Tuple[pd.Series, List[Dict]]]:
        self.log.info(f"🚀 Starting engine '{self.instance_id}' in '{self.mode}' mode...")
        
        await self._initialize_client_and_context()
        self.strategy.initialize_components()
        self._create_handler_map()
        
        self._running.set()
        
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self.stop()))
        loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self.stop()))
        
        self.updater_tasks = [u.start() for u in self.strategy.updaters]
        
        results = None
        main_loop_task = None
        if self.mode == 'backtest':
            main_loop_task = asyncio.create_task(self._run_backtest_loop())
        else:
            main_loop_task = asyncio.create_task(self._run_live_loop())

        await main_loop_task
        results = main_loop_task.result()
        
        await self.stop()
        return results

    async def _run_backtest_loop(self) -> Optional[Tuple[pd.Series, List[Dict]]]:
        updaters_done = asyncio.gather(*self.updater_tasks)
        
        while self._running.is_set():
            if updaters_done.done() and self.event_bus.empty():
                self.log.info("All updaters finished and event bus is empty. Ending backtest.")
                break
            
            try:
                event = await self.event_bus.get()
                await self.dispatch(event)
            except asyncio.CancelledError:
                break
        
        self.log.info("Backtest loop finished. Returning results for reporting.")
        portfolio = self.context.get('portfolio')
        if not portfolio or not portfolio.equity_curve:
            self.log.warning("Equity curve is empty. No trades were made.")
            return pd.Series(dtype=float), []
        
        equity_df = pd.DataFrame(portfolio.equity_curve).set_index('timestamp')
        returns = equity_df['equity'].pct_change().dropna()
        trades = [asdict(trade) for trade in portfolio.trades]
        return returns, trades

    async def _run_live_loop(self):
        while self._running.is_set():
            try:
                event = await asyncio.wait_for(self.event_bus.get(), timeout=1.0)
                await self.dispatch(event)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
        await asyncio.gather(*self.updater_tasks, return_exceptions=True)

    async def dispatch(self, event: Event):
        if event.type == EventType.MARKET and isinstance(self.client, BacktestClient):
                self.client.tick(event.data['time'])
        handlers = self.handler_map.get(event.type, [])
        if handlers:
            await asyncio.gather(*(p.process(event) for p in handlers))

    async def stop(self):
        if not self._running.is_set(): return
        self.log.info(f"🛑 Stopping engine '{self.instance_id}'...")
        self._running.clear()
        
        await asyncio.gather(*(u.stop() for u in self.strategy.updaters), return_exceptions=True)
        
        for task in self.updater_tasks:
            if not task.done():
                task.cancel()
        
        self.log.info("Engine has stopped.")