# eops/examples/live_config.py
# An example configuration file for running a strategy in live mode.

from eops.exchanges import EopsLiveExchange
from .live_strategy_example import LiveExampleStrategy # Import from the example strategy file

# --- Exchange Configuration ---
# These parameters will be passed to the EopsLiveExchange instance.
EXCHANGE_CLASS = EopsLiveExchange
EXCHANGE_PARAMS = {
    "base_url": "http://127.0.0.1:8000/api/v1",
    # IMPORTANT: These should be loaded securely, e.g., from environment variables.
    # For this example, we hardcode them. Replace with your actual keys.
    "api_key": "YOUR_API_KEY_HERE",
    "secret_key": "YOUR_SECRET_KEY_HERE",
}

# --- Strategy Configuration ---
STRATEGY_CLASS = LiveExampleStrategy
STRATEGY_PARAMS = {
    "instrument": "CRYPTO:BTC@USDT_SPOT",
    "order_amount": "0.001",
    "topics_to_subscribe": [
        "tickers:CRYPTO:BTC@USDT_SPOT",
        # You can also subscribe to your own private order updates
    ]
}

# --- Engine Configuration (Optional) ---
ENGINE_PARAMS = {}