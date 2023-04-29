from dataclasses import dataclass
from lark.tree import Meta
from splashAST import *
from splashAST import _Ty, _Node

from liquidtypes import transformRefinement, liquid_type_check

from enum import Enum

RETURN="#return"

class_name = lambda c: c.__class__.__name__

class Errors(Enum):
    MetaInfo:str = "[{}, {}] to [{}, {}]"
    IlOperator:str = "Illegal Operation: Can't use {} operator for types {} and {}"
    Unexpected:str = "Unexpected {}: Exptected {} but got {}"


class TypeCheckingError(Exception):

    def __init__(self, message: str, meta:Meta = None):
        # print("META:", meta)
        if not meta :
            super().__init__(message)
        else:
            super().__init__(message, Errors.MetaInfo.value.format(meta.line, meta.column, meta.end_line, meta.end_column))



@dataclass
class Context():
    """
        Context for typechecking,
        Makes use of a stack, for every subsequent scope, 
         another dictionary is added to the pile, thus allowing shadowing

    """

    stack = [{}]

    def get_type(self, name:str):

        for scope in self.stack.__reversed__():
            if name in scope:
                return scope[name]
        raise TypeCheckingError(f"Identifier {name} not in context")
    


    def set_type(self, name:str, value):
        self.stack[-1][name] = value
        
    def has_var(self, name:str):
        for scope in self.stack.__reversed__():
            if name in scope:
                return True
        return False
    
    def is_var_in_current_scope(self, name:str):
        return name in self.stack[-1]


    def enter_scope(self):
        self.stack.append({})

    def exit_scope(self):
        self.stack.pop()




def is_subtype(ctx:Context, this, that ):


    print("\nis subtype was changed to accommodate liquid types\n")

    # print("This class:", this[0].__class__)
    # print("That class:", that[0].__class__)

    if isinstance(this, Array) and isinstance(that, Array):
        return is_subtype(ctx, this.innerType, that.innerType)
    
    sc: bool = issubclass(this[0].__class__, that[0].__class__)

    if not sc:
        return False
    ref_check = liquid_type_check(ctx, this, that)
    return sc and ref_check




def infer_type(ctx:Context, expr:Expression) -> _Ty:
    
    # print("INFERING:", expr)
    if isinstance(expr, Neg) or isinstance(expr, Not):
        transformRefinement(Neg, *infer_type(ctx, expr.expr))
        return infer_type(ctx, expr.expr)
    
    elif isinstance(expr, Add):        
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        if isinstance(l_ty, String) or isinstance(l_ty, String):
            return (String(), None)
        
        forbidden = (Bool, Void)

        if isinstance(l_ty, forbidden) or isinstance(r_ty, forbidden):
            raise TypeCheckingError(Errors.IlOperator.value.format("binary plus(+)",class_name(l_ty), class_name(r_ty)), meta=expr.meta)

        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return (Double(), None)
        else:
            return (Int(), None)
        
    elif isinstance(expr, Sub):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        forbidden = (String, Bool, Void)

        if isinstance(l_ty, forbidden) or isinstance(r_ty, forbidden):
            raise TypeCheckingError(
                Errors.IlOperator.value.format("binary minus", class_name(l_ty), class_name(r_ty) )
            )

        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return (Double(), None)
        else:
            return (Int(), None)

    elif isinstance(expr, Mul):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        forbidden = (String, Bool, Void)

        if isinstance(l_ty, forbidden) or isinstance(r_ty, forbidden):
            raise TypeCheckingError(Errors.IlOperator.value.format("multiplication (x)", class_name(l_ty), class_name(r_ty)))


        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return (Double(), None)
        else:
            return (Int(), None)
        
    elif isinstance(expr, Div):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        forbidden = (String, Bool, Void)

        if isinstance(l_ty, forbidden) or isinstance(r_ty, forbidden):
            raise TypeCheckingError(Errors.IlOperator.value.format(
                "division (/)", class_name(l_ty), class_name(r_ty)))

        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return (Double(), None)
        else:
            return (Int(), None)
    
    elif isinstance(expr, Mod):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        forbidden = (String, Bool, Void)

        if isinstance(l_ty, forbidden) or isinstance(r_ty, forbidden):
            raise TypeCheckingError(Errors.IlOperator.value.format("modulo (%)", class_name(l_ty), class_name(r_ty)))


        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return (Double(), None)
        else:
            return (Int(), None)

    elif isinstance(expr, And):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        if isinstance(l_ty, Bool) and isinstance(r_ty, Bool):
            return (Bool(), None)
        else:
            raise TypeCheckingError(Errors.IlOperator.value.format("Logical And (&&)", class_name(l_ty), class_name(r_ty)))

    elif isinstance(expr, Or):
        l_ty = infer_type(ctx, expr.l_expr)[0]
        r_ty = infer_type(ctx, expr.r_expr)[0]

        if isinstance(l_ty, Bool) and isinstance(r_ty, Bool):
            return (Bool(), None)
        else:
            raise TypeCheckingError(Errors.IlOperator.value.format("Logical And (&&)", class_name(l_ty), class_name(r_ty)))


    elif isinstance(expr, IndexAccess):

        indexed_exp_type = infer_type(ctx, expr.indexed)
        if not isinstance(indexed_exp_type[0], Array):
            raise TypeCheckingError("Expression not indexable")
        
        indexing_type = infer_type(ctx, expr.index)
        if not is_subtype(ctx, indexing_type, (Int(), None)):
            raise TypeCheckingError(Errors.Unexpected.value.format("Type", class_name(Int) , class_name(indexing_type)))

        return (indexed_exp_type[0].innerType, None)
        
    elif isinstance(expr, Literal):
        return (expr.type_, None)

    elif isinstance(expr, Var):
        return ctx.get_type(expr.name)

    elif isinstance(expr, FuncCall):
        return ctx.get_type(expr.called)
    
    elif isinstance(expr, str): # Just a name
        return ctx.get_type(expr)
    else:
        print(f"Can't infer type of expression {expr}")
        return (None, None)




def verify(ctx:Context, node):
    
    if isinstance(node, Program):
        for st in node.statements:
            verify(ctx, st)
    
    elif isinstance(node, FuncDef):
        
        ctx.set_type(node.name, value=(node.type_ ,node.refinement, *node.params.args))
        # print("Function call stored as:", ctx.get_type(node.name))
        ctx.enter_scope()

        ctx.set_type(RETURN, (node.type_, node.refinement))        
        for param in node.params.args:
            # print(f"Function Arg: {json.dumps(param, indent=2, cls=jsonAST)}")
            # print(f"Arg refinement: {param.refinement}")
            ctx.set_type(param.name, (param.type_, param.refinement))
        ctx.enter_scope()
        for st in node.block.statements:
            verify(ctx, st)
        ctx.exit_scope()
        ctx.exit_scope()

    elif isinstance(node, IfThenElse):
        if verify(ctx, node.test) != Bool:
            raise TypeCheckingError(f"If Condition: {node.test}, must be a boolean value")
        
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
        print(verify(ctx, node.l_expr), verify(ctx, node.r_expr))
        if infer_type(ctx, node.l_expr)[0] != infer_type(ctx, node.r_expr)[0]:
            raise TypeCheckingError(f"Operands ({node.l_expr}) and ({node.r_expr}) are not comparable")
        return Bool

    elif isinstance(node, Var):
        if not ctx.has_var(node.name):
            raise TypeCheckingError(f"Variable {node.name} not defined in current context")
        return ctx.get_type(node.name)[0]
    
    elif isinstance(node, VarDef):
        if ctx.is_var_in_current_scope(node.name):
            raise TypeCheckingError(f"Variable {node.name} already defined in current context")
        
        inf_ty = infer_type(ctx, node.value)

        if is_subtype(ctx, inf_ty, (node.type_,None)):
            ctx.set_type(node.name, (node.type_, None))
        else:
            raise TypeCheckingError(f"Variable Type Mismatch: Variable was declared as {node.type_} but assigned a value of {inf_ty}")
    
    elif isinstance(node, Neg):
        tmp = infer_type(ctx, node.expr)
        if not is_subtype(ctx, tmp , (Numeric(), None)):
            raise TypeCheckingError(f"Can't use unary minus on non-numeric types. Type used: {tmp}")
        return tmp
    
    elif isinstance(node, Return):

        expected = ctx.get_type(RETURN)
        # if node.value != None:
        #     actual = infer_type(ctx, node.value)
        # else:
        #     actual = Void()
        expr_type = infer_type(ctx, node.value)
        if not is_subtype(ctx, expr_type , expected):
            raise TypeCheckingError(f"Invalid Return Type: Expected {expected.__class__.__name__} but got {actual.__class__.__name__}", meta=node.meta)

    elif isinstance(node, VarDec):

        if ctx.is_var_in_current_scope(node.name):
            raise TypeCheckingError(f"Variable already declared in current context")
        ctx.set_type(node.name, (node.type_, None))

    elif isinstance(node, SetVal):

        name = None
        expected = None
        expected = infer_type(ctx, node.varToSet)
            
        if ctx.has_var( name ):
        
            actual = infer_type(ctx, node.value)
            if not is_subtype(ctx, actual, expected):
                raise TypeCheckingError(f"Type mismatch: Expected {expected} and got {actual}")
            
    elif isinstance(node, FuncCall):

        # print("NODE META:", json.dumps(node, indent=2, cls=jsonAST))

        if ctx.has_var(node.called): # If function is defined

            # print("Found", node.called, "in context")

            func_type, func_refinement, *args = ctx.get_type(node.called)
            print(args)

            if len(args) != len(node.args) :
                raise TypeCheckingError(f"Unexpected number of arguments for function {node.called}", meta=node.meta)
            
            for act, exp in zip(node.args, args):
                print("ARGS COMP:", act, exp)
                if not is_subtype(ctx, infer_type(ctx, act),  (exp.type_, exp.refinement)):
                    # print(f"Error checking: {act}::{exp}")
                    raise TypeCheckingError(f"Type mismatch: Expected {exp.type_.__class__.__name__} but got {infer_type(ctx, act)}", meta=node.meta)
        else:
            raise TypeCheckingError(f"Function {node.called} not defined.")
    
    elif isinstance(node, While):
        
       
        if verify(ctx, node.condition) != Bool:
            raise TypeCheckingError(f"While condition must be of type {Bool}")
        
        ctx.enter_scope()
        for stmt in node.block.statements:
            verify(ctx, stmt)
        ctx.exit_scope()

    elif isinstance(node, Literal):
        return infer_type(ctx, node)
        

    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")

    # print("Last Context: ", json.dumps(ctx.stack, indent=4, cls=jsonAST))