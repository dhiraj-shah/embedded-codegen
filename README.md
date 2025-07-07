# embedded-codegen

**Embedded peripheral code generator**

`embedded-codegen` takes a YAML description of the board's peripherals (GPIO, UART, Timer, etc.) and emits:

* **C code** + Device Tree blobs (`.dts`)
* **AST** dumps (JSON)
* **LLVM IR** (`.ll`)
* **Object files** (`.o`) for x86, STM32 (ARM Cortex‑M), i.MX7 (AArch64)

---

## Features

* **Declarative input**: describe pins, modes, baudrates, timers in YAML
* **Pluginable peripherals**: GPIO, UART, Timer; easily extendable to I²C, SPI, CAN…
* **Multi‐backend**:

  * Templated C & DTS via Jinja2
  * AST -> LLVM IR via `llvmlite`
  * IR -> object (`.o`) with `llvm` or `llc` + `clang`
* **Flexible CLI**:

  * `--emit-ast`, `--emit-ir`, `--emit-obj`
  * `--target {x86,stm32,imx7}`
  * `-v`/`-vv` verbosity

---

## Quickstart

### 1. Prerequisites

Before installing and running embedded-codegen, ensure you have:

* Python ≥3.9

* LLVM toolchain on your PATH:
    clang, llc (for IR-to-object)
    Optionally llvm-as / llvm-dis if you work with bitcode

* Cross‑compilers for your targets on PATH:
    * x86: gcc, g++
    * STM32 (ARM Cortex‑M): arm-none-eabi-gcc, arm-none-eabi-g++
    * i.MX7 (AArch64/Linux): aarch64-linux-gnu-gcc, aarch64-linux-gnu-g++

* Python package dependencies (installed by pip or Poetry):
    * jinja2, pydantic, typer, rich, pyyaml
    * Optional: llvmlite (only if you plan to emit LLVM IR or object files via llvmlite)


### 2. Installation 

    From PyPI (future release)
    * pip install embedded-codegen

    From local wheel (now)
    After building your package (python -m build), install directly:
    
    pip install dist/embedded_codegen-0.1.0-py3-none-any.whl
    # include dev extras for testing & docs:
    pip install dist/embedded_codegen-0.1.0-py3-none-any.whl[dev]

    Note: your dist/ directory must be up‑to‑date. Run:

    ```bash
    python -m build
    ```
    outside any other virtualenv to produce fresh .whl + .tar.gz files.

### 3. Example config (`config.yaml`)

```yaml
name: demo_board
gpio:
  - pin: PA0
    mode: output
    pull: up
    speed: high
uart:
  - name: UART1
    tx: PA9
    rx: PA10
    baudrate: 115200
timer:
  - name: TIM2
    prescaler: 7999
    period: 1000
```

### 4. Generate C + DTS

```bash
embedded-codegen --config config.yaml --template-dir core/templates --out-dir out --target stm32

embedded-codegen --config config.yaml --template-dir core/templates --out-dir out-imx7 --target imx7 -vv 
```

### 5. Adding Make-based ELF build in out/
Once C and DTS files are generated into your --out-dir directory, you can:

```bash
cd out
make
```
This will compile *.c/*.h/*.dts and builds firmware.elf. Flash or analyze with your usual tools.

Be sure your Makefile.j2 template defines an elf target pointing at firmware.elf.

### 6. Emit AST / LLVM IR / Object

```bash
# AST JSON
embedded-codegen --config config.yaml --emit-ast ast.json --target x86

# IR text
embedded-codegen --config config.yaml --emit-ir out.ll --target x86

# object file
embedded-codegen --config config.yaml --emit-obj out.o --target stm32
```

---

## Documentation

We use **Sphinx** to generate API docs from doc‐strings. To bootstrap:

```text
docs/
  conf.py       <- Sphinx config (enable `autodoc`)
  index.rst     <- Table of contents
  modules.rst   <- `.. automodule:: core.config`
```

Then:

```bash
pip install sphinx sphinx-autodoc
cd docs && make html
```

---

## Architecture & Design

1. **YAML -> Pydantic**: `core/config.py` loads & validates board schema.
2. **Templates**: `core/generator.py` drives Jinja2 engine to render C / DTS files.
3. **AST layer**: `core/ast/` builds a minimal AST (module -> functions -> calls).
4. **IR Codegen**: `core/ir/codegen.py` lowers AST -> LLVM IR via `llvmlite.ir`.
5. **Backend**: `core/ir/backend.py` compiles IR -> object bytes using `llvmlite.binding` (native) or calls out to `llc`/`clang`.

This layered approach:

* Keeps C/DTS and IR paths orthogonal.
* Allows future direct LLVM -> firmware images (linker scripts).
* Scales by adding new peripheral plugins in `core/peripherals/` and new AST nodes.

---

## Contributing

* Follow **PEP8** and **Black** formatting.
* Add new peripherals under `core/peripherals`, update Pydantic schemas.
* Write tests in `tests/` and run `pytest -vv`.
* Update `CHANGELOG.md` and version in `pyproject.toml`.

---

## License

MIT © Dhiraj Shah

