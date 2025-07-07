from llvmlite import ir, binding as llvm
from core.ast.nodes import ASTModule, ASTCall

"""
Lower an ASTModule to LLVM IR using llvmlite.ir.
"""
def ast_to_llvm_ir(ast_mod: ASTModule, module_name: str,
                   target_triple: str = None,
                   cpu: str = None,
                   features: str = None) -> ir.Module:
    """
    Lower our AST to a textual LLVM IR module.
    Declares externs for gpio_init, uart_init, timer_init,
    then defines `int main()` which invokes them.

     Args:
        ast_mod (ASTModule): The AST to lower.
        module_name (str): The LLVM module name (e.g. board name).
        triple (str): Target triple string (e.g., x86_64-pc-linux-gnu).
        data_layout (str): Data layout string from TargetMachine.

     Returns:
        ir.Module: LLVM IR module ready to compile or dump.
    """

    llvm_mod = ir.Module(name=module_name)

    if target_triple:
        # make sure the binding is initialized
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # pick up the right target and build a TM to get the data layout
        tgt = llvm.Target.from_triple(target_triple)
        tm  = tgt.create_target_machine(cpu=cpu, features=features or "")
        llvm_mod.triple     = target_triple
        llvm_mod.data_layout = tm.target_data

    # declare extern void gpio_init()/uart_init()/timer_init()
    void = ir.VoidType()
    extern_ty = ir.FunctionType(void, [])
    gpio_fn = ir.Function(llvm_mod, extern_ty, name="gpio_init")
    uart_fn = ir.Function(llvm_mod, extern_ty, name="uart_init")
    timer_fn = ir.Function(llvm_mod, extern_ty, name="timer_init")

    # define `int main() { ... }`
    i32 = ir.IntType(32)
    main_ty = ir.FunctionType(i32, [])
    main_fn = ir.Function(llvm_mod, main_ty, name="main")
    entry_bb = main_fn.append_basic_block(name="entry")
    builder = ir.IRBuilder(entry_bb)

    # walk AST
    for fn in ast_mod.functions:
        for stmt in fn.body:
            if isinstance(stmt, ASTCall):
                if stmt.func_name == "gpio_init":
                    builder.call(gpio_fn, [])
                elif stmt.func_name == "uart_init":
                    builder.call(uart_fn, [])
                elif stmt.func_name == "timer_init":
                    builder.call(timer_fn, [])

    # return 0
    builder.ret(ir.Constant(i32, 0))
    return llvm_mod

