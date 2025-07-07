# Import the base registry
from .base import PERIPHERAL_REGISTRY

# Import each plugin so the decorator runs
from . import gpio
from . import uart
from . import timer
