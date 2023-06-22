from enum import Enum
from lark.tree import Meta

from typechecking.context import Context

from core.splash_ast import jsonAST
from core.splash_ast import Expression
from core.splash_ast import _Ty

# from typechecking.liquid import liquid_type_check

from core.splash_ast import ( # AST Nodes

    Program,
    FuncDec, FuncDef, FuncArgs, FuncCall,
    VarDec, VarDef, Variable,
    IfThenElse,
    Comparison,
    ArrayDef,
    Block, 

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



from core.splash_ast import ( # Types and Statics
    
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

    if isinstance(this, Array) and isinstance(that, Array):
        return is_subtype(ctx, this.innerType, that.innerType)
    
    sc: bool = this == that
    if not sc:
        return False
    return sc 


def infer_type(ctx: Context, expr: Expression) -> _Ty:

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
        if not isinstance(indexed_exp_type, (Array, ArrayDef)):
            raise TypeCheckingError(f"Expression of type {indexed_exp_type} is not indexable")

        indexing_type = infer_type(ctx, expr.index)
        if not (t_int == indexing_type):
            raise TypeCheckingError(
                Errors.Unexpected.value.format("Type", t_int, indexing_type))

        expr.final_ty = indexed_exp_type.innerType
        return indexed_exp_type.innerType

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
    
    elif isinstance(expr, ArrayDef):
        acc_type = infer_type(ctx, expr.elems[0])
        for i, el in enumerate(expr.elems[1:]):
            tmp = infer_type(ctx, el)
            if not acc_type == tmp: # != not defined, sorry
                raise TypeCheckingError(message=Errors.Unexpected.value.format("Array Element", acc_type, tmp) ,meta=expr.meta)
        expr.final_type = acc_type
        return Array(expr.final_type)
        

    elif isinstance(expr, Comparison):

        lex, rex = (verify(ctx, expr.l_expr), verify(ctx, expr.r_expr))

        if not (lex == rex):
            raise TypeCheckingError(
                f"Operands ({expr.l_expr}) and ({expr.r_expr}) are not comparable")
        
        expr.types = (lex, rex)

        return t_bool

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
            ctx.set_type(param.name, param.type_)
        ctx.enter_scope()
        for st in node.block.statements:
            verify(ctx, st)
        ctx.exit_scope()

        find_func_return(node)
        
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
        expr_type = infer_type(ctx, node.value) if node.value != None else t_void

        if not is_subtype(ctx, expr_type, expected):
            raise TypeCheckingError(
                f"Invalid Return Type: Expected {expected} but got {expr_type}", meta=node.meta)

        return RETURN

    elif isinstance(node, VarDec):

        if ctx.is_var_in_current_scope(node.name):
            raise TypeCheckingError(
                f"Variable {node.name}:{node.type_} already declared in current context")
        ctx.set_type(node.name, node.type_)

    elif isinstance(node, SetVal):

        expected = verify(ctx, node.varToSet)
        actual = verify(ctx, node.value)
    
        if not is_subtype(ctx, actual, expected):
            raise TypeCheckingError(Errors.Unexpected.value.format("Type", expected, actual))
    

    elif isinstance(node, FuncCall):

        if ctx.has_var(node.called):  # If function is defined

            func_type, *args = ctx.get_type(node.called)
            ver_arg = [ verify(ctx, arg) for arg in node.args ]
            node.args_tys = ver_arg

            if node.called == "print":
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

    elif isinstance(node, Comparison):
    
        if not (verify(ctx, node.l_expr) == verify(ctx, node.r_expr)):
            raise TypeCheckingError(
                f"Operands ({node.l_expr}) and ({node.r_expr}) are not comparable")
        node.types = (verify(ctx, node.l_expr), verify(ctx, node.r_expr))
        return t_bool

        
    elif isinstance(node, (Literal, IndexAccess, Add, Sub, Mul, Div, Mod, And, Or, ArrayDef)):
        return infer_type(ctx, node)

    elif isinstance(node, BasicType):
        return node
    
    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")



def find_func_return(func_def:FuncDef):
    """
        Nodes that can have nested nodes, are primarily Blocks, but since blocks can't exist on their own:

        FuncDef
        IfThenElse x2
        While

        Mainly used to verify whether or not a function actually returns. Previously, if a function declared as type X returned type Y, that error would be flagged, but if the function never actually returned, it would not be flagged as an error.
    """
    return _find_ret_aux(func_def.block.statements, func_def.type_==t_void, func_meta=func_def.meta)


def _find_ret_aux(node_list, is_void, ind=0, func_meta=None):

    for i, st in enumerate(node_list):
        if isinstance(st, Return):
            return True
        if isinstance(st, IfThenElse):
            if is_void: # If the function is void, we don't care if it returns
                return True

            check_else_br = [] if st.else_do == None else st.else_do.statements 

            main_br_returns = _find_ret_aux(node_list[i+1:], is_void, func_meta=func_meta)
            then_br_returns = _find_ret_aux(st.then_do.statements, is_void, ind+1, func_meta=func_meta)
            else_br_returns = _find_ret_aux(check_else_br, is_void, ind+1, func_meta=func_meta)

            if main_br_returns: 
                return True
            else: # Main does not return
                if then_br_returns and else_br_returns:
                    return True
                else:
                    raise TypeCheckingError(f"Non-Void functions must always return a value", meta=func_meta) 
    

        if isinstance(st, While):
            while_br_returns = _find_ret_aux( st.block.statements, is_void, ind+1, func_meta=func_meta)
            main_br_returns = _find_ret_aux( node_list[i+1:], is_void, func_meta=func_meta)


            # I know this could be condensed into one statement, although I find
            # easier to read this way. Also space for other cases might be added as warnings
            # explaining why returning inside a while and not outside might bring problems
            if is_void and not while_br_returns and not main_br_returns:
                return True
            elif while_br_returns and main_br_returns:
                return True
            else:
                return False