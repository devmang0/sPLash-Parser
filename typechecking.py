from dataclasses import dataclass
from splashAST import *
from splashAST import _Ty, _Node

RETURN="#return"

class TypeError(Exception):

    def __init__(self, message: str, node: _Node = None) -> None:
        if node == None:
            super().__init__(message)
        else:
            super().__init__( f"Error found in {node.line}"+message)

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
        raise TypeError(f"Variable {name} not in context")
    


    def set_type(self, name:str, value:str):
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
    # print( "superclasses:", this.__mro__ )
    return issubclass(this.__class__, that.__class__) and liquid_type_check(ctx, this, that)
         

def infer_type(ctx:Context, expr:Expression):



    if isinstance(expr, Var):
        return ctx.get_type(expr.name).__class__

    elif is_subtype(ctx, expr, _Ty()):
        return expr.__class__

    return ctx.get_type(expr)


def liquid_type_check(ctx:Context, this, that) -> bool:
    print("Liquid types are not yet implemented")
    return True


    

def verify(ctx:Context, node):
    
    if isinstance(node, Program):
        for st in node.statements:
            verify(ctx, st)
    
    elif isinstance(node, FuncDef):
        ctx.enter_scope()
        ctx.set_type(RETURN, value=node.type_)
        for arg in node.args.args:
            ctx.set_type(arg.name, arg.type_)
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
        if infer_type(ctx, node.l_expr) != infer_type(ctx, node.r_expr):
            raise TypeError(f"Operands ({node.l_expr}) and ({node.r_expr}) are not comparable", node=node)
        return Bool

    elif isinstance(node, Var):
        if not ctx.has_var(node.name):
            raise TypeError(f"Variable {node.name} not defined in current context")
        return ctx.get_type(node.name)
    
    elif isinstance(node, VarDef):
        if ctx.is_var_in_current_scope(node.name):
            raise TypeError(f"Variable {node.name} already defined in current context")
    
    elif isinstance(node, Neg):
        tmp = infer_type(ctx, node.expr)
        if is_subtype(ctx, tmp , Numeric()):
            raise TypeError(f"Can't use unary minus on non-numeric types. Type used: {tmp}")
        return tmp
    
    elif isinstance(node, Return):

        expected = ctx.get_type(RETURN)
        actual = node.value

        if is_subtype(ctx, actual, expected):
            raise TypeError(
                f"Invalid Return Type: Expected: {expected} but got {actual}")

    elif isinstance(node, VarDec):

        if ctx.is_var_in_current_scope(node.name):
            raise TypeError(f"Variable already declared in current context")
        ctx.set_type(node.name, node.type_)

    elif isinstance(node, SetVal):

        name = None
        expected = None

        if isinstance(node.varToSet, IndexAccess):
            name, expected = infer_type(ctx, node)
        elif isinstance(node.varToSet, str):
            name = node.varToSet
            expected = ctx.get_type(name)
            
        if ctx.has_var( name ):
        
            actual = infer_type(ctx, node.value)
            if not is_subtype(ctx, actual, expected):
                raise TypeError(f"Type mismatch: Expected {expected} and got {actual}")
            


    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")
        return False

    return True