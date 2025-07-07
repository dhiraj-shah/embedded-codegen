import logging
from pathlib import Path
import yaml
from pydantic import BaseModel, ValidationError
from typing import List, Optional

log = logging.getLogger(__name__)

class GPIO(BaseModel):
    pin: str
    mode: str
    pull: Optional[str] = None
    speed: Optional[str] = None
    alt_func: Optional[str] = None

class UART(BaseModel):
    name: str
    tx: str
    rx: str
    baudrate: int

class Timer(BaseModel):
    name: str
    prescaler: int
    period: int

"""
Load & validate board YAML into Pydantic model.
"""

class BoardConfig(BaseModel):
     """
    Schema for the board under test.

    Attributes:
        name: Identifier for the board.
        gpio, uart, timer: Lists of peripheral configs.
    """
    name: str
    gpio: List[GPIO] = []
    uart: List[UART] = []
    timer: List[Timer] = []


def load_config(path: Path) -> BoardConfig:

     """Load and validate a YAML board config.

    Args:
        path: Path to the YAML file defining name, gpio, uart, timer lists.

    Returns:
        A `BoardConfig` instance with validated fields.

    Raises:
        yaml.YAMLError: if the YAML is invalid.
        ValidationError: if required fields are missing/invalid.
    """

    log.debug("Opening YAML config at %s", path)
    with open(path, "r") as f:
        try:
            raw = yaml.safe_load(f)
        except yaml.YAMLError as ye:
            log.error("YAML parse error in %s: %s", path, ye)
            raise

    if not isinstance(raw, dict):
        log.error("Top-level YAML is not a mapping")
        raise yaml.YAMLError("Config must be a mapping at the top level")

    try:
        cfg = BoardConfig(**raw)
    except ValidationError as ve:
        log.error("Config validation error: %s", ve)
        raise

    log.info("Config %r validated successfully", cfg.name)
    return cfg

