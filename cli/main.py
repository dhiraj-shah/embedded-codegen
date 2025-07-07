#!/usr/bin/env python3

import argparse
import sys
import logging
import json
from pathlib import Path

from core.config     import load_config
from core.generator  import CodeGenerator
from core.ir_generator import LLVMIRGenerator

VERSION = "2.0.0"

# Predefined target configurations for object emission
TARGET_CONFIG = {
    "x86":   {"triple": "x86_64-pc-linux-gnu",    "cpu": "generic",    "features": ""},
    "stm32": {"triple": "armv7-none-eabi",       "cpu": "cortex-m3",  "features": "+thumb2"},
    "imx7":  {"triple": "aarch64-none-linux-gnu","cpu": "generic",    "features": ""},
}

"""
Command‐line entry for Embedded Codegen.
Handles config loading, templates, AST/IR/obj emission, and standard codegen.
"""

def main():

    """
    Parse CLI args, configure logging, dispatch to codegen or AST/IR backends.

    Args:
        config: Path to board YAML.
        template_dir: Directory of Jinja2 templates.
        out_dir: Output directory for C/DTS files.
        target: One of {x86, stm32, imx7}.
        emit_ast: Path to dump JSON AST.
        emit_ir: Path to dump LLVM IR.
        emit_obj: Path to output object file.
        llvm_ir: Flag to emit textual IR via Jinja templates.
        verbose: Verbosity level (-v/-vv).

    Returns:
        Exit code (0 success, non-zero on error).
    """

    parser = argparse.ArgumentParser(
        description="Embedded Peripheral Code Generator"
    )

    # Core options
    parser.add_argument("--config",      required=True, help="Path to YAML board config")
    parser.add_argument("--template-dir", default="templates",
                        help="Template directory for C code generation")
    parser.add_argument("--out-dir",     default="out",
                        help="Output directory for generated code")
    parser.add_argument("--target",      choices=TARGET_CONFIG.keys(),
                        help="Target platform (required for codegen or object emission)")
    parser.add_argument("-v", "--verbose",
                        action="count", default=0,
                        help="Increase verbosity (use -vv for DEBUG)")
    parser.add_argument("--version",
                        action="version", version=f"%(prog)s v{VERSION}")

    # AST / IR / Object flags
    parser.add_argument("--emit-ast", help="Dump the in-memory AST to JSON")
    parser.add_argument("--emit-ir",  help="Emit LLVM IR text to file")
    parser.add_argument("--emit-obj", help="Compile IR to an object file")

    # Legacy “run full C->IR pipeline” flag
    parser.add_argument("--llvm-ir", action="store_true",
                        help="After C codegen, run the LLVM-IR pipeline")

    args = parser.parse_args()

    # --target is only optional if just dumping AST or IR.
    if not (args.emit_ast or args.emit_ir) and not args.target:
        parser.error("--target is required for code generation or object emission")

    # Logging setup 
    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("embedded-codegen")
    log.debug("CLI args: %s", vars(args))

    try:
        # 1) Load + validate board config
        cfg = load_config(Path(args.config))
        log.info(
            "Loaded board config: %s (GPIO=%d, UART=%d, TIMER=%d)",
            cfg.name, len(cfg.gpio), len(cfg.uart), len(cfg.timer),
        )

        # 2) If any of the AST/IR/OBJ flags are set, run the AST->IR->OBJ sub-pipeline:
        if args.emit_ast or args.emit_ir or args.emit_obj:
            from core.ast.builder import build_ast
            from core.ir.codegen   import ast_to_llvm_ir
            from core.ir.backend   import init_llvm, compile_module

            # Build an in-memory AST
            ast_mod = build_ast(cfg)

            # Dump AST?
            if args.emit_ast:
                with open(args.emit_ast, "w") as f:
                    json.dump(ast_mod, f, default=lambda o: o.__dict__, indent=2)
                log.info("AST dumped to %s", args.emit_ast)
                sys.exit(0)

            # Convert AST -> LLVM IR
            tc     = TARGET_CONFIG[args.target]
            irr_mod = ast_to_llvm_ir(
                ast_mod,
                module_name=cfg.name,
                target_triple=tc["triple"],
                cpu=tc["cpu"],
                features=tc["features"],
            )
            ir_text = str(irr_mod)

            # Dump IR?
            if args.emit_ir:
                Path(args.emit_ir).write_text(ir_text)
                log.info("LLVM IR written to %s", args.emit_ir)
                sys.exit(0)

            # Emit object?
            if args.emit_obj:
                init_llvm()
                obj = compile_module(
                    ir_text,
                    target_triple=tc["triple"],
                    cpu=tc["cpu"],
                    features=tc["features"],
                )
                Path(args.emit_obj).write_bytes(obj)
                log.info("Object file emitted to %s", args.emit_obj)
                sys.exit(0)

        # 3) Otherwise, fall back to C codegen (and optional IR pipeline)
        if args.llvm_ir:
            log.info(">>> Stage 1: C codegen for target %s", args.target)
            CodeGenerator(cfg,
                          Path(args.template_dir),
                          Path(args.out_dir),
                          args.target).generate()

            log.info(">>> Stage 2: LLVM IR pipeline for target %s", args.target)
            LLVMIRGenerator(cfg,
                            Path(args.out_dir),
                            args.target).generate()

        else:
            log.info(">>> C codegen for target %s", args.target)
            CodeGenerator(cfg,
                          Path(args.template_dir),
                          Path(args.out_dir),
                          args.target).generate()

    except Exception as e:
        log.critical("Error: %s", e, exc_info=True)
        # raise a non-zero exit code
        sys.exit(1)


if __name__ == "__main__":
    main()

