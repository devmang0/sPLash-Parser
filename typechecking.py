from dataclasses import dataclass
from lark.tree import Meta
from splashAST import *
from splashAST import _Ty, _Node

from enum import Enum

RETURN="#return"


class TypeError(Exception):

    def __init__(self, message: str, meta:Meta = None):

        # print("META:", meta)
        if not meta :
            super().__init__(message)
        else:
            super().__init__(
                f"Error found in {meta.line},{meta.column}:{message}")

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
        raise TypeError(f"Identifier {name} not in context")
    


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
    print(f"{this.__class__.__name__} subclass of {that.__class__.__name__}?:", issubclass(this.__class__, that.__class__))
    sc: bool = issubclass(this.__class__, that.__class__)

    if isinstance(this, Array) and isinstance(that, Array):
        return is_subtype(ctx, this.innerType, that.innerType)

    if not sc:
        return False
    ref_check = liquid_type_check(ctx, this, that)
    return sc and ref_check


def liquid_type_check(ctx:Context, this, that) -> bool:
    # TODO - implement actual liquid typechecking
    # print("Liquid types are not yet implemented")
    return True

def infer_type(ctx:Context, expr:Expression) -> _Ty:

    # print("INFERING:", expr)

    if isinstance(expr, Neg) or isinstance(expr, Not) :
        return infer_type(ctx, expr.expr)
    
    elif isinstance(expr, Add):
        
        l_ty = infer_type(ctx, expr.l_expr)
        r_ty = infer_type(ctx, expr.r_expr)

        if isinstance(l_ty, String) or isinstance(l_ty, String):
            return String()
        
        if isinstance(l_ty, (Bool, Void)) or isinstance(r_ty, (Bool, Void)):
            raise TypeError(f"Can't use plus operand with Bool or Void types")

        if isinstance(l_ty, Double) or isinstance(r_ty,  Double):
            return Double()
        else:
            return Int()
        

        # TODO - Infer Stronger Type

    elif isinstance(expr, IndexAccess):

        indexed_exp_type = infer_type(ctx, expr.indexed)
        print("Indexed_exp_type: ", indexed_exp_type)
        if not isinstance(indexed_exp_type, Array):
            raise TypeError("Expression not indexable")
        
        index_type = infer_type(ctx, expr.index)
        if not isinstance(index_type, Int):
            raise TypeError("Indexing expression must be an Int")

        return indexed_exp_type.innerType
        
    elif isinstance(expr, Literal):
        return expr.type_

    elif isinstance(expr, Var):
        return ctx.get_type(expr.name)

    elif isinstance(expr, FuncCall):
        func_sign: FuncDef = ctx.get_type(expr.called)
        return func_sign.type_
    else:
        # print(f"Can't infer type of expression {expr}")
        return ctx.get_type(expr)




def verify(ctx:Context, node):
    
    if isinstance(node, Program):
        for st in node.statements:
            verify(ctx, st)
    
    elif isinstance(node, FuncDef):
        
        ctx.set_type(node.name, value=node)
        ctx.enter_scope()

        ctx.set_type(RETURN, node.type_)        
        for param in node.params.args:
            ctx.set_type(param.name, param.type_)
        ctx.enter_scope()
        for st in node.block.statements:
            verify(ctx, st)
        ctx.exit_scope()
        ctx.exit_scope()

    elif isinstance(node, IfThenElse):
        if verify(ctx, node.test) != Bool:
            raise TypeError(f"If Condition: {node.test}, must be a boolean value")
        
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
        # print(verify(ctx, node.l_expr), verify(ctx, node.r_expr))
        if infer_type(ctx, node.l_expr) != infer_type(ctx, node.r_expr):
            raise TypeError(f"Operands ({node.l_expr}) and ({node.r_expr}) are not comparable")
        return Bool

    elif isinstance(node, Var):
        if not ctx.has_var(node.name):
            raise TypeError(f"Variable {node.name} not defined in current context")
        return ctx.get_type(node.name)
    
    elif isinstance(node, VarDef):
        if ctx.is_var_in_current_scope(node.name):
            raise TypeError(f"Variable {node.name} already defined in current context")
        
        inf_ty = infer_type(ctx, node.value)
        print(f"var_def: {node.name} = {inf_ty}, expected {node.type_}")
        if is_subtype(ctx, inf_ty, node.type_):
            ctx.set_type(node.name, node.type_)
        else:
            raise TypeError(f"Variable Type Mismatch: Variable was declared as {node.type_} but assigned a value of {inf_ty}")
    
    elif isinstance(node, Neg):
        tmp = infer_type(ctx, node.expr)
        if not is_subtype(ctx, tmp , Numeric()):
            raise TypeError(f"Can't use unary minus on non-numeric types. Type used: {tmp}")
        return tmp
    
    elif isinstance(node, Return):

        expected = ctx.get_type(RETURN)
        if node.value != None:
            actual = infer_type(ctx, node.value)
        else:
            actual = Void()

        if not is_subtype(ctx, actual, expected):
            raise TypeError(f"Invalid Return Type: Expected {expected.__class__.__name__} but got {actual.__class__.__name__}", meta=node.meta)

    elif isinstance(node, VarDec):

        if ctx.is_var_in_current_scope(node.name):
            raise TypeError(f"Variable already declared in current context")
        ctx.set_type(node.name, node.type_)

    elif isinstance(node, SetVal):

        name = None
        expected = None

        expected = infer_type(ctx, node.varToSet)
            
        if ctx.has_var( name ):
        
            actual = infer_type(ctx, node.value)
            if not is_subtype(ctx, actual, expected):
                raise TypeError(f"Type mismatch: Expected {expected} and got {actual}")
            
    elif isinstance(node, FuncCall):

        # print("NODE META:", json.dumps(node, indent=2, cls=jsonAST))

        if ctx.has_var(node.called): # If function is defined

            # print("Found", node.called, "in context")

            fd:FuncDef = ctx.get_type(node.called)

            if len(fd.params.args) != len(node.args) :
                raise TypeError(f"Unexpected number of arguments for function {node.called}", meta=node.meta)
            
            for act, exp in zip(node.args, fd.params.args):
                if not is_subtype(ctx, infer_type(ctx, act),  exp.type_):
                    print(f"Error checking: {act}::{exp}")
                    raise TypeError(f"Type mismatch: Expected {exp.type_.__class__.__name__} but got {infer_type(ctx, act)}", meta=node.meta)
        else:
            raise TypeError(f"Function {node.called} not defined.")
    
    elif isinstance(node, While):
        
       
        if verify(ctx, node.condition) != Bool:
            raise TypeError(f"While condition must be of type {Bool}")
        
        ctx.enter_scope()
        for stmt in node.block.statements:
            verify(ctx, stmt)
        ctx.exit_scope()

    elif isinstance(node, Literal):
        return infer_type(ctx, node)
        

    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")

    # print("Last Context: ", json.dumps(ctx.stack, indent=4, cls=jsonAST))