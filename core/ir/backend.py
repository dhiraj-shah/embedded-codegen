import subprocess
import tempfile
import os
from pathlib import Path


"""
Initialize LLVM and compile LLVM IR to object code using llvmlite.binding.
"""

def init_llvm():
    """
    Initialize the LLVM binding, registering all available targets.
    """
    pass


def compile_module(
    llvm_ir: str,
    target_triple: str,
    cpu: str = "generic",
    features: str = ""
) -> bytes:
    """
    Emit an object file by invoking the external `llc` tool.

    Args:
        llvm_ir: Textual LLVM IR.
        target_triple: The target triple (e.g. 'x86_64-pc-linux-gnu', 'armv7-none-eabi').
        cpu: CPU identifier for -mcpu.
        features: Comma-separated CPU features for -mattr.

    Returns:
        Raw object code bytes.
    """
    # Write IR to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as ir_file:
        ir_file.write(llvm_ir.encode("utf-8"))
        ir_path = ir_file.name

    # Create a temporary file for the output object
    fd, obj_path = tempfile.mkstemp(suffix=".o")
    os.close(fd)

    try:
        # Build llc command
        cmd = [
            "llc",
            "-filetype=obj",
            "-mtriple", target_triple,
            "-mcpu", cpu,
        ]
        if features:
            cmd.extend(["-mattr", features])
        cmd.extend(["-o", obj_path, ir_path])

        # Invoke llc to compile IR to object file
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read and return the generated object code
        return Path(obj_path).read_bytes()
    finally:
        # Clean up temporary files
        for p in (ir_path, obj_path):
            try:
                Path(p).unlink()
            except OSError:
                pass

