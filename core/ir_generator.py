import shutil
import datetime
import subprocess
from pathlib import Path
from core.config import BoardConfig
import logging

log = logging.getLogger(__name__)

class LLVMIRGenerator:
    def __init__(self, config: BoardConfig, out_dir: Path, target: str):
        self.config = config
        self.out_dir = out_dir
        self.target = target

    def _clang_target(self) -> str:
        return {
            "stm32": "armv7e-m-none-eabi",
            "imx7":  "armv7-none-linux-gnueabihf",
            "x86":   "x86_64-pc-linux-gnu",
        }[self.target]

    def generate(self):
        log.info("Starting LLVM-IR pipeline in %s", self.out_dir)
        now = datetime.datetime.now()

        # 1) Recreate a clean IR directory
        ir_dir = self.out_dir / "ir"
        if ir_dir.exists():
            shutil.rmtree(ir_dir)
        ir_dir.mkdir(parents=True)

        # 2) Ensure bin/ exists
        bin_dir = self.out_dir / "bin"
        bin_dir.mkdir(exist_ok=True)

        src_dir = self.out_dir / "src"
        inc_dir = self.out_dir / "include"

        # 3) Compile each C -> LLVM bitcode (.bc)
        for c_file in sorted(src_dir.glob("*.c")):
            bc = ir_dir / f"{c_file.stem}.bc"
            log.info("Compiling %s -> %s", c_file.name, bc.name)
            subprocess.run([
                "clang",
                "-target", self._clang_target(),
                "-I", str(inc_dir),
                "-emit-llvm",
                "-c", str(c_file),
                "-o", str(bc),
            ], check=True)

        # 4) Link *only* those fresh .bc files -> firmware.bc
        leaf_bc = sorted(ir_dir.glob("*.bc"))  # now only *.bc, no firmware.bc yet
        linked_bc = ir_dir / "firmware.bc"
        log.info("Linking %d BC modules -> firmware.bc", len(linked_bc.name))
        log.info("Linking %s", linked_bc.name)
        subprocess.run(
            ["llvm-link", *map(str, leaf_bc), "-o", str(linked_bc)],
            check=True
        )

        # 5) Lower IR -> object file
        obj = ir_dir / "firmware.o"
        log.info("Lowering IR -> %s", str(obj.name))
        subprocess.run([
            "llc",
            "-filetype=obj",
            "-mtriple=" + self._clang_target(),
            "-relocation-model=pic", 
            str(linked_bc),
            "-o", str(obj),
        ], check=True)

        # 6) Link object -> final ELF
        elf = bin_dir / "firmware.elf"
        log.info("Linking object -> %s", elf.name)
        subprocess.run([
            "clang",
            "-target", self._clang_target(),
            "-o", str(elf),
            str(obj),
        ], check=True)

        log.info("LLVM IR pipeline complete: %s", elf)

