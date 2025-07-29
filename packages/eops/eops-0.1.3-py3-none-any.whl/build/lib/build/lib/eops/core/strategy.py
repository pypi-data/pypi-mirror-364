# eops/core/strategy.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, TYPE_CHECKING

# FIX: Import handlers' base classes
from .handler import BaseUpdater, BaseEventHandler, BaseDecider, BaseExecutor

if TYPE_CHECKING:
    from .engine import Engine

class BaseStrategy(ABC):
    def __init__(self, engine: 'Engine', context: Dict[str, Any], params: Dict[str, Any]):
        self.engine = engine
        self.context: Dict[str, Any] = context
        self.params: Dict[str, Any] = params
        
        self.log = self.engine.log
        self.event_bus = self.engine.event_bus
        self.mode = self.engine.mode
        
        self.shared_state: Dict[str, Any] = {}

        # Initialize empty lists. Components will be created later.
        self.updaters: List[BaseUpdater] = []
        self.event_handlers: List[BaseEventHandler] = []
        self.deciders: List[BaseDecider] = []
        self.executors: List[BaseExecutor] = []

        self.log.info(f"Strategy '{self.__class__.__name__}' object created in '{self.mode}' mode.")

    def initialize_components(self):
        """
        Creates and initializes all UADE components.
        This method is called by the engine after the context is fully populated.
        """
        self.log.info(f"Initializing components for strategy '{self.__class__.__name__}'...")
        self.updaters = self._create_updaters()
        self.event_handlers = self._create_event_handlers()
        self.deciders = self._create_deciders()
        self.executors = self._create_executors()
        
        self._validate_components()
        self.log.info("All strategy components initialized successfully.")
        
    def _validate_components(self):
        if not self.updaters: raise ValueError("A strategy must have at least one Updater.")
        if not self.deciders: raise ValueError("A strategy must have at least one Decider.")
        if not self.executors: raise ValueError("A strategy must have at least one Executor.")

    @staticmethod
    def describe_params() -> List[Dict[str, Any]]:
        return []

    @abstractmethod
    def _create_updaters(self) -> List[BaseUpdater]: pass
    def _create_event_handlers(self) -> List[BaseEventHandler]: return []
    @abstractmethod
    def _create_deciders(self) -> List[BaseDecider]: pass
    @abstractmethod
    def _create_executors(self) -> List[BaseExecutor]: pass