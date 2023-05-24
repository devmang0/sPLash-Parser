from enum import Enum
from lark.tree import Meta

from typechecking.context import Context

from splash_ast import jsonAST
from splash_ast import Expression
from splash_ast import _Ty

from typechecking.liquid import liquid_type_check

from splash_ast import ( # AST Nodes

    Program,
    FuncDec, FuncDef, FuncArgs, FuncCall,
    VarDec, VarDef, Variable,
    IfThenElse,
    Comparison,

    SetVal, 
    While,

    Literal,
    Var,

    IndexAccess, 

    Return,
    Refinement,

    Not, Neg, # Unary Log/Arithmetic
    And, Or,  # Binary Logical
    Add, Sub, Mul, Div, Mod, # Binary Arithemetic 

)



from splash_ast import ( # Types and Statics
    
    BasicType,
    Array,

    t_int,
    t_double,
    t_bool,
    t_string,
    t_void
)

RETURN = "#return"


def class_name(c): return c.__class__.__name__


class Errors(Enum):
    MetaInfo: str = "in lines[{}, {}] to [{}, {}]"
    IlOperator: str = "Illegal Operation: Can't use {} operator for types {} and {}"
    Unexpected: str = "Unexpected {}: Exptected {} but got {}"


class TypeCheckingError(Exception):

    def __init__(self, message: str, meta: Meta = None):
        # print("META:", meta)
        if not meta:
            super().__init__(message)
        else:
            super().__init__(message+" "+Errors.
                                        MetaInfo.
                                        value.
                                        format( meta.line,
                                                meta.column, 
                                                meta.end_line, 
                                                meta.end_column
                                              )
                            )



def is_subtype(ctx:Context, this, that ):


    # print("\nis subtype was changed to accommodate liquid types\n")

    # print("This class:", this[0].__class__)
    # print("That class:", that[0].__class__)

    if isinstance(this, Array) and isinstance(that, Array):
        return is_subtype(ctx, this.innerType, that.innerType)
    
    sc: bool = this == that
    # print(f"{this} == {that}?: {this == that}")
    if not sc:
        return False
    ref_check = liquid_type_check(ctx, this, that)
    return sc and ref_check


def infer_type(ctx: Context, expr: Expression) -> _Ty:

    # print("INFERING:", expr)
    if isinstance(expr, Neg) or isinstance(expr, Not):
        return infer_type(ctx, expr.expr)

    elif isinstance(expr, (Add, Sub, Mul, Div, Mod)):

        l_ty = infer_type(ctx, expr.l_expr)
        r_ty = infer_type(ctx, expr.r_expr)

        if l_ty == t_string or r_ty == t_string:
            expr.final_ty = t_string
            return t_string

        forbidden = (t_bool, t_void)

        if l_ty in forbidden or r_ty in forbidden:
            raise TypeCheckingError(Errors.IlOperator.value.format(
                expr, l_ty, r_ty), meta=expr.meta)

        if l_ty == t_double or r_ty == t_double:

            expr.final_ty = t_double
            return t_double
        else:
            expr.final_ty = t_int
            return t_int

    elif isinstance(expr, (And, Or)):
        l_ty = infer_type(ctx, expr.l_expr)
        r_ty = infer_type(ctx, expr.r_expr)

        if l_ty == t_bool and r_ty == t_bool:
            return t_bool
        else:
            raise TypeCheckingError(Errors.IlOperator.value.format(
                expr, l_ty, r_ty))


    elif isinstance(expr, IndexAccess):

        indexed_exp_type = infer_type(ctx, expr.indexed)
        if not isinstance(indexed_exp_type, Array):
            raise TypeCheckingError("Expression not indexable")

        indexing_type = infer_type(ctx, expr.index)
        if not (t_int == indexing_type):
            raise TypeCheckingError(
                Errors.Unexpected.value.format("Type", t_int, indexing_type))

        return indexed_exp_type.innerType

    # elif isinstance(expr, Literal):
    #     return (expr.type_, None)

    elif isinstance(expr, Var):
        var_ty = ctx.get_type(expr.name)
        expr.type_ = var_ty
        return var_ty

    elif isinstance(expr, FuncCall):
        return ctx.get_type(expr.called)

    elif isinstance(expr, str):  # Just a name
        return ctx.get_type(expr)
    
    elif isinstance(expr, BasicType):
        return expr
    
    elif isinstance(expr, Literal):
        return expr.type_
    else:
        print(f"Can't infer type of expression {expr}")
        return None


def verify(ctx: Context, node):

    if isinstance(node, Program):

        remaining: list = []

        for st in node.statements:
            if isinstance(st, (FuncDef, FuncDec, VarDef, VarDec)):
                verify(ctx, st)
            else:
                remaining.append(st)

        for st in remaining:
            verify(ctx, st)

    elif isinstance(node, FuncDef):

        ctx.set_type(node.name, value=(node.type_, *node.params.args))

        ctx.enter_scope()

        ctx.set_type(RETURN, node.type_)
        for param in node.params.args:
            # print(f"Function Arg: {json.dumps(param, indent=2, cls=jsonAST)}")
            # print(f"Arg refinement: {param.refinement}")
            ctx.set_type(param.name, param.type_)
        ctx.enter_scope()
        for st in node.block.statements:
            verify(ctx, st)
        ctx.exit_scope()
        ctx.exit_scope()

    elif isinstance(node, IfThenElse):
        if verify(ctx, node.test) != t_bool:
            raise TypeCheckingError(
                f"If Condition: {node.test}, must be a boolean value")

        ctx.enter_scope()
        for st in node.then_do.statements:
            verify(ctx, st)
        ctx.exit_scope()
        if node.else_do != None:
            ctx.enter_scope()
            for st in node.else_do.statements:
                verify(ctx, st)
            ctx.exit_scope()

    elif isinstance(node, Comparison):
        # print( verify(ctx, node.l_expr), 
        #        verify(ctx, node.r_expr), 
        #        infer_type(ctx, node.l_expr), 
        #        infer_type(ctx, node.r_expr)
        #      )

        if not (verify(ctx, node.l_expr) == verify(ctx, node.r_expr)):
            raise TypeCheckingError(
                f"Operands ({node.l_expr}) and ({node.r_expr}) are not comparable")
        node.types = (verify(ctx, node.l_expr), verify(ctx, node.r_expr))
        return t_bool

    elif isinstance(node, Var):
        if not ctx.has_var(node.name):
            raise TypeCheckingError(
                f"Variable {node.name} not defined in current context")
        var_ty = ctx.get_type(node.name)
        node.type_ = var_ty
        return var_ty

    elif isinstance(node, VarDef):
        if ctx.is_var_in_current_scope(node.name):
            raise TypeCheckingError(
                f"Variable {node.name} already defined in current context")

        var_ty = verify(ctx, node.value)
        if is_subtype(ctx, var_ty, node.type_):
            ctx.set_type(node.name, var_ty)
        else:
            raise TypeCheckingError(
                f"Variable Type Mismatch: Variable was declared as {node.type_} but assigned a value of {var_ty}")

    elif isinstance(node, Neg):
        tmp = infer_type(ctx, node.expr)
        if (not tmp == t_int) and (not tmp == t_double) : # Not equals 
            raise TypeCheckingError(
                f"Can't use unary minus on non-numeric types. Type used: {tmp}")
        return tmp

    elif isinstance(node, Return):

        expected = ctx.get_type(RETURN)
        expr_type = None
        if node.value != None:
            expr_type = infer_type(ctx, node.value)
        else:
            expr_type = t_void
        if not is_subtype(ctx, expr_type, expected):
            raise TypeCheckingError(
                f"Invalid Return Type: Expected {expected[0].__class__.__name__} but got {expr_type[0].__class__.__name__}", meta=node.meta)

    elif isinstance(node, VarDec):

        if ctx.is_var_in_current_scope(node.name):
            raise TypeCheckingError(
                f"Variable {node.name}:{node.type_} already declared in current context")
        ctx.set_type(node.name, node.type_)

    elif isinstance(node, SetVal):

        name = None
        expected = None
        expected = infer_type(ctx, node.varToSet)

        if ctx.has_var(name):

            actual = verify(ctx, node.value)
            if not is_subtype(ctx, actual, expected):
                raise TypeCheckingError(Errors.Unexpected.value.format("Type", expected, actual))

    elif isinstance(node, FuncCall):

        if ctx.has_var(node.called):  # If function is defined
            # print("Found", node.called, "in context")
            func_type, *args = ctx.get_type(node.called)
            # print(args)
            ver_arg = [ verify(ctx, arg) for arg in node.args ]
            node.args_tys = ver_arg

            if node.called == "print":
                # print(f"[{node.called}]VER_ARGS:", ver_arg)
                # print(f"[{node.called}]ARGS:", node.args)
                return func_type

            if len(args) != len(node.args):
                raise TypeCheckingError(Errors.Unexpected.value.format( f"number of arguments for function {node.called}", len(args), len(node.args)), meta=node.meta)

            for act, exp in zip(node.args, args):
                
                verified = verify(ctx, act)
                if not is_subtype(ctx, verified,  exp.type_):
                    raise TypeCheckingError(Errors.Unexpected.value.format("Type", exp.type_, verified), meta=node.meta)
            
            return func_type
        
        else:
            raise TypeCheckingError(f"Function {node.called} not defined.")

    elif isinstance(node, While):

        if verify(ctx, node.condition) != t_bool:
            raise TypeCheckingError(
                f"While condition must be of type {t_bool}")

        ctx.enter_scope()
        for stmt in node.block.statements:
            verify(ctx, stmt)
        ctx.exit_scope()

    elif isinstance(node, (Literal, IndexAccess, Add, Sub, Mul, Div, Mod, And, Or)):
        return infer_type(ctx, node)

    elif isinstance(node, BasicType):
        return node
    
    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")
