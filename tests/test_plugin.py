import pytest
from core.peripherals.base import PERIPHERAL_REGISTRY

def test_registry_contains_defaults():
    # these should be registered at import-time
    for key in ("GPIO", "UART", "TIMER"):
        assert key in PERIPHERAL_REGISTRY, f"{key} missing from registry"

