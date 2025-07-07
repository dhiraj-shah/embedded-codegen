import yaml
from pathlib import Path
import pytest
from core.config import load_config
from core.generator import CodeGenerator

def test_codegen_creates_files(tmp_path, sample_cfg, tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    cfg = load_config(sample_cfg)
    cg = CodeGenerator(cfg, Path("core/templates"), out, "x86")
    cg.generate()

    # expected outputs
    assert (out / "src" / "gpio.c").exists()
    assert (out / "include" / "gpio.h").exists()
    assert (out / "src" / "uart.c").exists()
    assert (out / "src" / "timer.c").exists()
    assert (out / "Makefile").exists()
    # main.c should include gpio_init call
    main = (out / "src" / "main.c").read_text()
    assert "gpio_init" in main and "uart_init" in main and "timer_init" in main

