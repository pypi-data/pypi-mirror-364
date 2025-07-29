# eops/core/handler/updater.py
from abc import ABC, abstractmethod
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..strategy import BaseStrategy

class BaseUpdater(ABC):
    def __init__(self, strategy: 'BaseStrategy'):
        self.strategy = strategy
        self.log = self.strategy.log
        self.event_bus = self.strategy.event_bus
        self._task: asyncio.Task = None
        self._should_stop = asyncio.Event()

    # ... (no other changes here, it will use event_bus.put which is low-priority)
    def is_alive(self) -> bool:
        return self._task and not self._task.done()

    @abstractmethod
    async def run(self):
        pass

    def start(self) -> asyncio.Task:
        self.log.info(f"Creating task for updater '{self.__class__.__name__}'...")
        self._should_stop.clear()
        self._task = asyncio.create_task(self.run())
        return self._task

    async def stop(self):
        self.log.info(f"Stopping updater '{self.__class__.__name__}'...")
        if self._task and not self._task.done():
            self._should_stop.set()
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except asyncio.TimeoutError:
                self.log.warning(f"Updater '{self.__class__.__name__}' did not stop gracefully within 5 seconds.")
                self._task.cancel()
            except asyncio.CancelledError:
                pass