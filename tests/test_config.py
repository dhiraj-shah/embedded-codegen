import yaml
from pathlib import Path
import pytest
from core.config import load_config, BoardConfig

def test_load_flat_config(tmp_path):
    data = {
        "name": "demo",
        "gpio": [],
        "uart": [],
        "timer": []
    }
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data))
    cfg = load_config(p)
    assert isinstance(cfg, BoardConfig)
    assert cfg.name == "demo"
    assert cfg.gpio == [] and cfg.uart == [] and cfg.timer == []

