# eops/clients/__init__.py
from typing import Dict, Any, Type

from .base import BaseClient
# We will re-add these as they get refactored
# from .binance import BinanceClient
# from .okx import OkxClient
# from .backtest import BacktestClient
from eops.utils.logger import log

# We keep the map for future use, but it's temporarily empty
CLIENT_MAP: Dict[str, Type[BaseClient]] = {
    # "binance": BinanceClient,
    # "okx": OkxClient,
    # "backtest": BacktestClient,
}

def get_client(client_name: str, params: Dict[str, Any] = None) -> BaseClient:
    """Factory function to get an instance of an exchange client."""
    if params is None:
        params = {}
        
    client_class = CLIENT_MAP.get(client_name.lower())
    
    if client_class:
        log.info(f"Instantiating client for '{client_name}'...")
        return client_class(**params)
    else:
        # Import the backtest client dynamically to avoid circular dependencies if it uses the factory
        if client_name.lower() == 'backtest':
            from .backtest import BacktestClient
            log.info("Instantiating client for 'backtest'...")
            return BacktestClient(**params)
            
        supported_exchanges = ", ".join(CLIENT_MAP.keys())
        raise ValueError(
            f"Client '{client_name}' is not supported. Supported clients are: [backtest, {supported_exchanges}]"
        )