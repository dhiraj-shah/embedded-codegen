import yaml
from pathlib import Path
import pytest
from core.config import load_config
from core.generator import CodeGenerator

def render_dir(tmp_path, cfg_dict, target="x86"):
    p = tmp_path / "cfg.yaml"
    p.write_text(yaml.safe_dump(cfg_dict))
    cfg = load_config(p)
    out = tmp_path / "out"
    cg = CodeGenerator(cfg, Path("core/templates"), out, target)
    cg.generate()
    return out

def test_no_gpio_section(tmp_path):
    cfg = {"name":"demo", "uart":[], "timer":[]}
    out = render_dir(tmp_path, cfg)
    assert not (out/"src"/"gpio.c").exists()

def test_multiple_gpio_entries(tmp_path):
    cfg = {
      "name":"demo",
      "gpio":[
        {"pin":"PA0","mode":"output","pull":"up","speed":"high"},
        {"pin":"PA1","mode":"input","pull":"down","speed":"low"}
      ]
    }
    out = render_dir(tmp_path, cfg)
    code = (out/"src"/"gpio.c").read_text()
    # two configure_pin calls
    assert code.count("configure_pin") == 2
    assert "PA0" in code and "PA1" in code

