# eops/clients/errors.py
class ExchangeError(Exception):
    """Base exception for all exchange-related errors."""
    pass

class AuthenticationError(ExchangeError):
    """Raised when authentication fails (e.g., invalid API key)."""
    pass

class InsufficientFunds(ExchangeError):
    """Raised when an operation cannot be completed due to lack of funds."""
    pass

class InvalidOrder(ExchangeError):
    """Raised for invalid order parameters (e.g., amount, price)."""
    pass

class OrderNotFound(ExchangeError):
    """Raised when a requested order does not exist."""
    pass

class NetworkError(ExchangeError):
    """Raised for network-related issues (e.g., timeouts, connection errors)."""
    pass

class NotSupported(ExchangeError):
    """Raised when the exchange does not support the requested feature."""
    pass