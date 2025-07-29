# eops/instruments.py
import re
from dataclasses import dataclass
from typing import Optional

class InstrumentError(ValueError):
    """Custom exception for instrument parsing errors."""
    pass

@dataclass(frozen=True)
class Instrument:
    """
    A structured, standardized representation of a tradable instrument.
    This is the heart of the Eops Instrument ID (EID) system.
    """
    asset_class: str
    base_symbol: str
    quote_currency: str
    market: Optional[str] = None
    product_type: Optional[str] = 'SPOT' # SPOT, PERP, FUTURES, OPTION

    # --- For complex derivatives ---
    expiry: Optional[str] = None       # e.g., '240927'
    strike: Optional[float] = None     # for options
    option_type: Optional[str] = None  # 'C' or 'P'

    def to_eid(self) -> str:
        """Constructs the Eops Instrument ID string from the structured data."""
        # Base part: ASSET_CLASS:BASE_SYMBOL
        base_part = f"{self.asset_class.upper()}:{self.base_symbol.upper()}"
        
        # Market part (optional): .MARKET
        market_part = f".{self.market.lower()}" if self.market else ""
        
        # Quote part: @QUOTE_CURRENCY
        quote_part = f"@{self.quote_currency.upper()}"
        
        # Product type part: _PRODUCT_TYPE
        product_part = f"_{self.product_type.upper()}"

        return f"{base_part}{market_part}{quote_part}{product_part}"

def parse_eid(eid: str) -> Instrument:
    """
    Parses a Eops Instrument ID (EID) string into a structured Instrument object.
    
    Format: ASSET_CLASS:BASE_SYMBOL[.MARKET]@QUOTE_CURRENCY_PRODUCT_TYPE
    Examples:
        - CRYPTO:BTC.binance@USDT_SPOT
        - CRYPTO:BTC-240927@USDT_FUTURES
        - HK_STOCK:00700.HKEX@HKD_SPOT
    """
    # Regex to capture the main components of the EID
    # 1: asset_class, 2: base_symbol, 3: .market (optional), 4: quote, 5: _product_type
    pattern = re.compile(r"^([A-Z_]+):([^@]+?)(\.[a-z0-9]+)?@([A-Z]{2,})_([A-Z]+)$")
    match = pattern.match(eid)

    if not match:
        raise InstrumentError(f"Invalid EID format: '{eid}'")

    asset_class, base_symbol_raw, market_raw, quote, product_type = match.groups()

    market = market_raw[1:] if market_raw else None

    # --- Further parse base_symbol for derivative info ---
    expiry, strike, option_type = None, None, None
    base_symbol = base_symbol_raw

    if product_type == 'OPTION':
        # e.g., BTC-241227-80000-C
        option_parts = base_symbol_raw.split('-')
        if len(option_parts) == 4:
            base_symbol, expiry, strike_str, option_type = option_parts
            strike = float(strike_str)
        else:
            raise InstrumentError(f"Invalid option format in EID base symbol: '{base_symbol_raw}'")
    elif product_type == 'FUTURES':
        # e.g., BTC-240927
        future_parts = base_symbol_raw.split('-')
        if len(future_parts) == 2:
            base_symbol, expiry = future_parts
        else:
            raise InstrumentError(f"Invalid futures format in EID base symbol: '{base_symbol_raw}'")

    return Instrument(
        asset_class=asset_class,
        base_symbol=base_symbol,
        market=market,
        quote_currency=quote,
        product_type=product_type,
        expiry=expiry,
        strike=strike,
        option_type=option_type,
    )