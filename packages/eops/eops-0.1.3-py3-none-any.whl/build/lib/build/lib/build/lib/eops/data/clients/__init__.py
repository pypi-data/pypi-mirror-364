# eops/data/clients/__init__.py
from .base import BaseDataClient
from .binance import BinanceClient
from .okx import OkxClient

# Add other clients here as you implement them
# from .bybit import BybitClient

SUPPORTED_CLIENTS = {
    "binance": BinanceClient,
    "okx": OkxClient,
    # "bybit": BybitClient,
}

def get_data_client(exchange_id: str) -> BaseDataClient:
    """
    Factory function to get an instance of a data client for a given exchange.
    """
    client_class = SUPPORTED_CLIENTS.get(exchange_id.lower())
    
    if client_class:
        return client_class()
    else:
        raise ValueError(
            f"Exchange '{exchange_id}' is not supported for data download. "
            f"Supported exchanges are: {list(SUPPORTED_CLIENTS.keys())}"
        )