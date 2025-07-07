from dataclasses import dataclass
from typing import Any, List

"""
AST node definitions: module, function, statements, calls.
"""

class ASTNode:
    """Base class for all AST nodes."""
    pass

@dataclass
class ASTModule(ASTNode):
    """
    Top-level module containing functions.

    Attributes:
        functions: List of ASTFunction objects.
    """
    functions: List["ASTFunction"]

@dataclass
class ASTFunction(ASTNode):
    """
    Represents a function with parameters and a body of statements.

    Attributes:
        name: Function name.
        params: Parameter names.
        body: List of ASTStmt in the function body.
    """
    name: str
    params: List[str]
    body: List["ASTStmt"]

class ASTStmt(ASTNode):
    """Base class for statements."""
    pass

@dataclass
class ASTCall(ASTStmt):
    """
    Represents a call statement to an external init function.

    Attributes:
        func_name: Name of the function to call.
        args: List of arguments (unused here).
    """
    func_name: str
    args: List[Any]

