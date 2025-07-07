from core.config import BoardConfig
from core.ast.nodes import ASTModule, ASTFunction, ASTCall

"""
Build ASTModule from BoardConfig: one `main` with init calls.
"""

def build_ast(cfg: BoardConfig) -> ASTModule:
    """
    Create an ASTModule containing a single `main` function.
    The body contains ASTCall nodes for each enabled peripheral.

    Args:
        cfg: BoardConfig instance.

    Returns:
        ASTModule ready for IR generation.
    """
    stmts = []
    if cfg.gpio:
        stmts.append(ASTCall("gpio_init", []))
    if cfg.uart:
        stmts.append(ASTCall("uart_init", []))
    if cfg.timer:
        stmts.append(ASTCall("timer_init", []))

    main_fn = ASTFunction(name="main", params=[], body=stmts)
    return ASTModule(functions=[main_fn])

