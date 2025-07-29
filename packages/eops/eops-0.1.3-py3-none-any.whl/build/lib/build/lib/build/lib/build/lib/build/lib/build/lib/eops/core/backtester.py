# eops/core/backtester.py
import pandas as pd
import quantstats as qs
from typing import Dict, Any

from .engine import BaseEngine
from .event import EventType
from .portfolio import Portfolio
from .sim_exchange import SimulatedExchange
from queue import Empty

class BacktestEngine(BaseEngine):
    """
    The engine for backtesting strategies against historical data using
    the full UADE event-driven architecture.
    """
    def __init__(self, config: Dict[str, Any], report_path=None):
        # We need to initialize the parent BaseEngine first to get the logger.
        # This requires a bit of refactoring in how we pass args. We'll do a two-stage init.
        
        data_path = config.get("backtest_data_path")
        if not data_path:
             raise ValueError("`BACKTEST_DATA_PATH` must be specified in the config for backtesting.")
        
        try:
            full_data = pd.read_csv(data_path, parse_dates=['time'], index_col='time')
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found at {data_path}")
        
        engine_params = config.get("engine_params", {})
        initial_cash = float(engine_params.get("initial_cash", 10000.0))
        fee_rate = float(engine_params.get("fee_rate", 0.001))

        # We pass a temporary, incomplete context first to initialize the engine/logger.
        # This will be updated later.
        super().__init__(
            strategy_class=config["strategy_class"], 
            context={}, 
            params=config.get("strategy_params", {})
        )
        self.log.info("🔧 Initializing UADE-based Backtest Engine...")

        # Now, create the backtest-specific components
        self.report_path = report_path
        self.portfolio = Portfolio(initial_cash=initial_cash, log=self.log) # Pass logger to Portfolio
        self.exchange = SimulatedExchange(data=full_data, portfolio=self.portfolio, fee_rate=fee_rate)

        # Now, populate the strategy's context with the fully initialized components.
        self.strategy.context.update({
            "exchange": self.exchange,
            "portfolio": self.portfolio,
            "full_data": full_data,
            "backtest_data_path": data_path
        })

        self.updaters = self.strategy.updaters
        self.log.info("✅ Backtest Engine initialization complete.")

    def run(self):
        """Overrides BaseEngine.run() to handle the specific lifecycle of a backtest."""
        self.log.info(f"🚀 Starting backtest...")
        self.running = True
        self.start_event_sources() 
        
        while any(u._thread.is_alive() for u in self.updaters) or not self.event_bus.empty():
            try:
                event = self.event_bus.get(block=True, timeout=1.0)
            except Empty:
                if not any(u._thread.is_alive() for u in self.updaters):
                    break
                continue

            if event:
                if event.type == EventType.MARKET:
                    current_time = event.data['time']
                    try:
                        idx = self.exchange.data.index.get_loc(current_time)
                        self.exchange.tick(idx)
                    except KeyError:
                        self.log.error(f"Could not find time {current_time} in data index. Skipping tick.")
                        continue
                    
                    symbol = self.strategy.params.get("symbol", "UNKNOWN_SYMBOL")
                    price = self.exchange._get_current_price(symbol)
                    self.portfolio.update_equity(current_time, {symbol: price})
                
                self.dispatch(event)
        
        self.stop()
        self._generate_report()

    def _generate_report(self):
        """Generates and prints a performance report using quantstats."""
        self.log.info("📊 Generating performance report...")
        if not self.portfolio.equity_curve:
            self.log.warning("Equity curve is empty. No trades were made. Skipping report generation.")
            return

        equity_df = pd.DataFrame(self.portfolio.equity_curve).set_index('timestamp')
        returns = equity_df['equity'].pct_change().dropna()
        
        if returns.empty:
            self.log.warning("No returns were generated. Skipping report.")
            return

        self.log.info("\n--- Backtest Summary ---")
        try:
            # Use a buffer to capture the print output of qs.stats.display
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            with redirect_stdout(f):
                qs.stats.display(returns)
            s = f.getvalue()
            self.log.info(s)
        except Exception:
            # Fallback for older versions or other errors
            self.log.info(f"Sharpe Ratio: {qs.stats.sharpe(returns):.2f}")
            self.log.info(f"CAGR:               {qs.stats.cagr(returns)*100:.2f}%")
            self.log.info(f"Max Drawdown: {qs.stats.max_drawdown(returns)*100:.2f}%")
        self.log.info("----------------------\n")

        if self.report_path:
            try:
                qs.reports.html(returns, output=str(self.report_path), title=f'Eops Strategy Report')
                self.log.info(f"💾 Full HTML report saved to: {self.report_path}")
            except Exception as e:
                self.log.error(f"Failed to generate HTML report: {e}", exc_info=True)