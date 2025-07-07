import pytest
import yaml
from pathlib import Path
from core.config import load_config
from pydantic import ValidationError

def write(tmp_path, data):
    p = tmp_path / "cfg.yaml"
    p.write_text(data)
    return p

def test_missing_required_field(tmp_path):
    # name is required
    bad = write(tmp_path, yaml.safe_dump({
        # "name": "demo",  
        "gpio": [], "uart": [], "timer": []
    }))
    with pytest.raises(ValidationError) as exc:
        load_config(bad)
    assert "name" in str(exc.value)

def test_wrong_type(tmp_path):
    # gpio must be a list, not a string
    bad = write(tmp_path, yaml.safe_dump({
        "name": "demo",
        "gpio": "not-a-list"
    }))
    with pytest.raises(ValidationError) as exc:
        load_config(bad)
    # Pydantic v2 says "Input should be a valid list"
    assert "Input should be a valid list" in str(exc.value)

def test_invalid_yaml(tmp_path):
    # completely malformed YAML still ends up a dict -> missing "name"
    p = tmp_path / "bad.yaml"
    p.write_text(":::::::")
    with pytest.raises(ValidationError) as exc:
        load_config(p)
    assert "Field required" in str(exc.value)

