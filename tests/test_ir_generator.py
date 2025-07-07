import subprocess
from pathlib import Path
import pytest
from core.ir_generator import LLVMIRGenerator
from core.config import BoardConfig

@pytest.fixture(autouse=True)
def no_subprocess_run(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: calls.append(args[0]))
    return calls

def test_ir_pipeline_invokes_clang_and_llc(tmp_path, no_subprocess_run):
    # Prepare fake C sources + headers
    out = tmp_path / "out"
    (out / "src").mkdir(parents=True)
    (out / "include").mkdir()
    # minimal files
    (out/"src"/"main.c").write_text("int main() { return 0; }")
    (out/"include"/"config.h").write_text("#define ENABLE_NONE\n")

    cfg = BoardConfig(name="demo", gpio=[], uart=[], timer=[])
    irg = LLVMIRGenerator(cfg, out, "x86")
    irg.generate()

    cmds = no_subprocess_run
    # should see at least one clang, one llvm-link, one llc
    assert any("clang" in cmd[0] for cmd in cmds)
    assert any("llvm-link" in cmd[0] for cmd in cmds)
    assert any("llc" in cmd[0] for cmd in cmds)

