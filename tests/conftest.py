import yaml
import pytest
from pathlib import Path
from core.config import load_config, BoardConfig

@pytest.fixture
def sample_cfg(tmp_path):
    data = {
        "name": "tst",
        "gpio": [{"pin": "PA0", "mode": "output", "pull": "up", "speed": "high"}],
        "uart": [{"name": "UART1", "tx": "PA9", "rx": "PA10", "baudrate": 115200}],
        "timer": [{"name": "TIM2", "prescaler": 0, "period": 100}],
    }
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data))
    return p

