# eops/cli.py
import typer
import asyncio
import json
import matplotlib
matplotlib.use('Agg')
import quantstats as qs
from pathlib import Path
from datetime import datetime
import pandas as pd
from typing import Optional

from eops.utils.config_loader import load_config_from_file
from eops.core.engine import Engine
from eops.data.downloader import download_ohlcv_data, fix_ohlcv_data
from eops.utils.logger import log as framework_log, setup_logger
from eops.clients import get_client
from eops import __version__ # Use absolute import
# import sys # No longer needed
# sys.path.insert(0, str(Path.cwd())) # REMOVE THIS LINE

main_app = typer.Typer(help="Eops - A quantitative trading framework.")
data_app = typer.Typer(name="data", help="Tools for managing historical data.")
main_app.add_typer(data_app)

# ... (rest of the file remains the same)
def generate_report(returns: pd.Series, trades: list, report_dir: Path, strategy_name: str):
    """Generates a full backtest report, including HTML and a summary TXT file."""
    if returns.empty:
        framework_log.warning("No returns generated. Skipping report.")
        (report_dir / "summary.txt").write_text("Backtest completed with no trades or no returns generated.")
        return

    html_report_path = report_dir / "report.html"
    summary_txt_path = report_dir / "summary.txt"
    framework_log.info(f"📊 Generating backtest report in {report_dir}...")

    try:
        # Run in executor to avoid blocking the event loop if called from async context
        qs.reports.html(returns, output=str(html_report_path), title=f'{strategy_name} Report')
        framework_log.info(f"✅ HTML report saved to: {html_report_path}")
    except Exception as e:
        framework_log.error(f"Failed to generate HTML report: {e}", exc_info=True)

    try:
        def get_metric_value(metric_func, returns_series):
            res = metric_func(returns_series)
            return res.iloc[0] if isinstance(res, pd.Series) else res

        sharpe = get_metric_value(qs.stats.sharpe, returns)
        cagr = get_metric_value(qs.stats.cagr, returns)
        max_dd = get_metric_value(qs.stats.max_drawdown, returns)
        win_rate = get_metric_value(qs.stats.win_rate, returns) if not returns.empty else 0.0
        
        summary_text = (
            f"--- Strategy Performance Summary ---\n"
            f"Strategy: {strategy_name}\n"
            f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"----------------------------------\n\n"
            f"Key Metrics:\n"
            f"  - Annualized Return (CAGR): {cagr:.2%}\n"
            f"  - Sharpe Ratio:               {sharpe:.2f}\n"
            f"  - Max Drawdown:               {max_dd:.2%}\n"
            f"  - Win Rate:                   {win_rate:.2%}\n\n"
            f"Trade Statistics:\n"
            f"  - Total Trades:               {len(trades)}\n"
        )
        summary_txt_path.write_text(summary_text)
        framework_log.info(f"✅ Summary saved to: {summary_txt_path}")
    except Exception as e:
        framework_log.error(f"Failed to generate summary.txt: {e}", exc_info=True)

@main_app.command()
def run(
    config_file: Path = typer.Argument(..., help="Path to the Python configuration file."),
    report_dir: Optional[Path] = typer.Option(None, "--report-dir", "-r", help="Directory to save backtest reports."),
    log_file: Optional[Path] = typer.Option(None, "--log-file", "-l", help="Path to save instance logs.")
):
    """Run a trading strategy from a configuration file."""
    
    async def main():
        if log_file:
            setup_logger("framework", log_file)

        framework_log.info(f"🚀 Starting Eops runner via CLI...")
        try:
            config = load_config_from_file(config_file)
            
            if log_file:
                config['LOG_FILE'] = log_file

            engine = Engine(config)
            results = await engine.run() 

            if config.get("MODE") == 'backtest' and report_dir:
                report_dir.mkdir(parents=True, exist_ok=True)
                if results:
                    returns, trades = results
                    strategy_name = config.get("STRATEGY_CLASS").__name__
                    generate_report(returns, trades, report_dir, strategy_name)
                else:
                    (report_dir / "summary.txt").write_text("Backtest completed with no results to report.")
        except Exception as e:
            framework_log.error(f"🔥 An application error occurred: {e}", exc_info=True)
            raise typer.Exit(code=1)

    try:
        # Before running, we need to ensure the project's root is in the path
        # so that it can find the 'examples' module from the config file.
        # This is the correct way to handle it, rather than modifying sys.path in the global scope.
        import sys
        project_root = Path.cwd()
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        framework_log.info("Eops CLI run interrupted. Exiting.")


@data_app.command("update-markets")
def update_markets_command(exchange: str = typer.Argument(..., help="Exchange to update, e.g., 'binance' or 'okx'")):
    async def do_update():
        typer.echo(f"Updating market data for {exchange}...")
        client = get_client(exchange)
        markets = await client.fetch_markets()
        static_data = {}
        for eid, market in markets.items():
            static_data[eid] = {
                "id": market.id, "symbol": market.symbol, "active": market.active,
                "precision": market.precision, "limits": market.limits,
                "contract_size": str(market.contract_size),
            }
        # This needs a fix, client doesn't have _get_static_market_path
        # For now, let's assume a default path
        path = Path(f"./data/{exchange}_markets.json")
        path.parent.mkdir(exist_ok=True, parents=True)
        with open(path, 'w') as f:
            json.dump(static_data, f, indent=2, sort_keys=True)
        typer.secho(f"✅ Successfully updated and saved {len(static_data)} markets to {path}", fg=typer.colors.GREEN)
    asyncio.run(do_update())

@data_app.command("download")
def download_data_command(exchange: str, symbol: str, timeframe: str, since: str,
                          output: Path, until: Optional[str] = None):
    download_ohlcv_data(exchange_id=exchange, symbol=symbol, timeframe=timeframe, since=since, output_path=output, until=until)

@main_app.command()
def info():
    typer.echo(f"Eops Quant Trading Library v{__version__}")

if __name__ == "__main__":
    main_app()