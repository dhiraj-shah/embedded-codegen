import logging
from abc import ABC, abstractmethod
from jinja2 import Environment
from core.config import BoardConfig
from pathlib import Path

log = logging.getLogger(__name__)

# Global registry: name -> generator class
PERIPHERAL_REGISTRY: dict[str, type["PeripheralGenerator"]] = {}

def register_peripheral(name: str):
    """
    Class decorator to register a PeripheralGenerator
    under the given name.
    """
    def decorator(cls: type["PeripheralGenerator"]):
        log.debug("Registering peripheral plugin %s", name)
        PERIPHERAL_REGISTRY[name] = cls
        return cls
    return decorator

class PeripheralGenerator(ABC):
    """
    Abstract base for all peripheral codegens.
    """

    def __init__(
        self,
        config: BoardConfig,
        env: Environment,
        dirs: dict[str, Path],
        now,
    ):
        self.config = config      # Validated board config
        self.env = env            # Jinja2 environment
        self.dirs = dirs          # {"src": Path, "include": Path, ...}
        self.now = now            # Timestamp for headers

    @abstractmethod
    def should_generate(self) -> bool:
        """Return True if this peripheral is present in config."""
        ...

    @abstractmethod
    def generate(self) -> None:
        """Render headers & sources for this peripheral."""
        ...

