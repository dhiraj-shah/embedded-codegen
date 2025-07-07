import subprocess
import sys
from pathlib import Path
import pytest

PY = sys.executable
SCRIPT = Path(__file__).parent.parent / "cli" / "main.py"

def run_cli(args, tmp_path):
    cmd = [PY, str(SCRIPT), *args]
    # capture both stdout & stderr
    return subprocess.run(cmd, capture_output=True, text=True)

def test_missing_template_dir(tmp_path):
    bad_templates = tmp_path / "nope"
    out = tmp_path / "out"
    res = run_cli([
        "--config", "config.yaml",
        "--template-dir", str(bad_templates),
        "--out-dir", str(out),
        "--target", "x86"
    ], tmp_path)
    assert res.returncode != 0
    assert "TemplateNotFound" in (res.stderr + res.stdout)

def test_invalid_target_flag(tmp_path):
    res = run_cli(["--config", "config.yaml", "--target", "mips"], tmp_path)
    # argparse will exit with code 2 on invalid choice
    assert res.returncode == 2
    assert "invalid choice: 'mips'" in res.stderr

