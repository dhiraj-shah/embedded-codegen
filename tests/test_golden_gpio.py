import pytest
from pathlib import Path

from core.config import load_config
from core.generator import CodeGenerator

GOLDEN = Path(__file__).parent / "golden" / "gpio_expected.c"

def test_gpio_golden(tmp_path, sample_cfg, tmp_path_factory):
    # sample_cfg fixture comes from tests/test_codegen.py
    out = tmp_path_factory.mktemp("out")
    cfg = load_config(sample_cfg)
    cg = CodeGenerator(cfg, Path("core/templates"), out, "x86")
    cg.generate()

    generated = (out / "src" / "gpio.c").read_text().strip()
    expected  = GOLDEN.read_text().strip()

    # Skip the first two lines (timestamp / header)
    gen_lines = generated.splitlines()[2:]
    gold_lines = expected.splitlines()[2:]

    assert gen_lines == gold_lines

