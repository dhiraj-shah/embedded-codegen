import datetime
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from core.config import BoardConfig
import core.peripherals 
from core.peripherals.base import PERIPHERAL_REGISTRY

import logging
log = logging.getLogger(__name__)

"""
Core C & DTS code generator: reads BoardConfig, renders templates.
"""

class CodeGenerator:

    def __init__(
        """
            Initialize with config model, templates dir, output dir, target.

            Args:
                config: BoardConfig instance.
                template_dir: Path to Jinja2 root.
                out_dir: Path where generated files go.
                target: Target name for DTS injection.
        """
        self,
        config: BoardConfig,
        template_dir: Path,
        out_dir: Path,
        target: str,
    ):
        self.config = config
        self.target = target
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.out_dir = out_dir
        # define output subdirs
        self.dirs = {
            "src": out_dir / "src",
            "include": out_dir / "include",
            "build": out_dir / "build",
            "bin": out_dir / "bin",
            "dts": out_dir / "dts",
        }

    def _mk_dirs(self):
        for name, path in self.dirs.items():
            log.debug("Ensuring directory %s ->  %s", name, path)
            path.mkdir(parents=True, exist_ok=True)

    def _render(self, template_name: str, dest: Path, **ctx):
        log.debug("Rendering template %s -> %s", template_name, dest)
        tpl = self.env.get_template(template_name)
        dest.write_text(tpl.render(**ctx))
        log.info("Generated %s", dest)

    def _clean(self):
        for path in self.dirs.values():
            if path.exists():
                log.debug("Removing existing directory %s", path)
                shutil.rmtree(path)

    def generate(self):

        """
        Orchestrate Jinja rendering of all shared and peripheral templates.
        Raises TemplateNotFound if any `.j2` missing.
        """

        log.info("Starting C-code generation into %s", self.out_dir)
        # Base directory
        self.out_dir.mkdir(exist_ok=True)
        # Clean & recreate
        self._clean()
        self._mk_dirs()
        now = datetime.datetime.now()

        # 1) HAL and syscalls
        self._render(
            "shared/hal.h.j2", self.dirs["include"] / "hal.h", board=self.config, now=now
        )
        self._render(
            "shared/hal.c.j2", self.dirs["src"] / "hal.c", board=self.config, now=now
        )
        if self.target == "stm32":
            self._render(
                "shared/syscalls.c.j2",
                self.dirs["src"] / "syscalls.c",
                board=self.config,
                now=now,
            )

        print("Registered peripherals:", list(PERIPHERAL_REGISTRY.keys()))

        # 2) Peripheral plugins
        peripheral_meta = []
        for name, GenClass in PERIPHERAL_REGISTRY.items():
            gen = GenClass(self.config, self.env, self.dirs, now)
            if gen.should_generate():
                gen.generate()
                peripheral_meta.append({
                    "name": name,
                    "header": f"{name.lower()}.h",
                    "func": f"{name.lower()}_init()",
                })

        # 3) config.h
        self._render(
            "shared/config.h.j2",
            self.dirs["include"] / "config.h",
            peripherals=peripheral_meta,
            now=now,
        )

        # 4) main.c
        self._render(
            "shared/main.c.j2",
            self.dirs["src"] / "main.c",
            peripherals=peripheral_meta,
            now=now,
        )

        # 5) Makefile
        self._render(
            "shared/Makefile.j2",
            self.out_dir / "Makefile",
            board=self.config,
            target=self.target,
            peripherals=peripheral_meta,
            now=now,
        )

        # 6) Device Tree
        if self.target in ("stm32", "imx7"):
            tpl = f"targets/{self.target}/board.dts.j2"
            self._render(
                tpl,
                self.dirs["dts"] / f"{self.config.name}_{self.target}.dts",
                board=self.config,
                now=now,
            )

        log.info("C code + DTS generation complete!")

