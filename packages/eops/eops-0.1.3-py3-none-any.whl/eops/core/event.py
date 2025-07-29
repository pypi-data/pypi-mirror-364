# eops/core/event.py
from enum import Enum
from typing import Any, Dict
import asyncio
from collections import deque

class EventType(Enum):
    """
    Enumeration of all possible event types in the system.
    """
    # Market Events
    MARKET = 'MARKET'             # A new kline/bar is available
    TICKER = 'TICKER'             # A new ticker price update is available
    PUBLIC_TRADE = 'PUBLIC_TRADE' # A new public trade has occurred on the exchange
    
    # Signal Events
    SIGNAL = 'SIGNAL'         # A strategy logic has generated a trading signal
    
    # Order Lifecycle Events
    ORDER = 'ORDER'           # A request to place a new order
    FILL = 'FILL'             # A private order has been filled (or partially filled)
    
    # Informational Events
    HEARTBEAT = 'HEARTBEAT'   # A regular time-based event, e.g., every second


class Event:
    """
    Base class for all event objects. It defines the type and optional data payload.
    """
    def __init__(self, event_type: EventType, data: Any = None):
        """
        Initializes the event.
        
        Args:
            event_type: The type of the event, from the EventType enum.
            data: A dictionary payload containing event-specific information.
        """
        self.type = event_type
        self.data: Dict[str, Any] = data if data is not None else {}

    def __str__(self):
        # A more informative string representation
        # Truncate long data previews
        items_preview = list(self.data.items())[:3]
        data_preview = ', '.join(f"{k}={v}" for k, v in items_preview)
        if len(self.data) > 3:
            data_preview += ', ...'
        return f"Event(type={self.type.name}, data={{{data_preview}}})"

class AsyncDeque:
    """A simple async wrapper around collections.deque for priority queue simulation."""
    def __init__(self):
        self._deque = deque()
        self._new_item = asyncio.Event()

    def empty(self) -> bool:
        """Checks if the deque is empty."""
        return not self._deque

    async def get(self) -> Event:
        """Asynchronously get an item from the left of the deque."""
        while self.empty():
            await self._new_item.wait()
        
        if self.empty(): # Check again in case of race condition on wakeup
             return await self.get()

        self._new_item.clear()
        return self._deque.popleft()

    def put_nowait(self, item: Event):
        """Add an item to the left (high priority)."""
        self._deque.appendleft(item)
        self._new_item.set()

    async def put(self, item: Event):
        """Add an item to the right (low priority)."""
        self._deque.append(item)
        self._new_item.set()