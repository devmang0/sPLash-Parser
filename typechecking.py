from dataclasses import dataclass
from lark.tree import Meta
from splashAST import *
from splashAST import _Ty, _Node

RETURN="#return"

class TypeError(Exception):

    def __init__(self, message: str, meta:Meta = None):

        print("META:", meta)

        if not meta :
            super().__init__(message)
        else:
            super().__init__(f"Error found in {meta.line},{meta.column}: ", message)

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
    


    def set_type(self, name:str, value:str, refinement:Refinement=None):
        self.stack[-1][name] = {"type": value, "ref":refinement}
        
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
    print(f"{this.__class__.__name__} subclass of {that.__class__.__name__}?:",
          issubclass(this.__class__, that.__class__))
    return issubclass(this.__class__, that.__class__) and liquid_type_check(ctx, this, that)


def liquid_type_check(ctx: Context, this, that) -> bool:

    print(this, that)
    print("Liquid types are not yet implemented")
    
    return True

def infer_type(ctx:Context, expr:Expression) -> _Ty:

    # print("INFERING EXPR TYPE:", expr)

    if isinstance(expr, IndexAccess):
        if ctx.has_var(expr.name):
            return ctx.get_type(expr.name).innerType
        
    elif isinstance(expr, Literal):
        return expr.type_

    elif isinstance(expr, Var):
        return ctx.get_type(expr.name)

    elif isinstance(expr, FuncCall):
        func_sign: FuncDef = ctx.get_type(expr.called)
        return func_sign.type_
    
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
        print(verify(ctx, node.l_expr), verify(ctx, node.r_expr))
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
        ctx.set_type(node.name, node.type_)
    
    elif isinstance(node, Neg):
        tmp = infer_type(ctx, node.expr)
        if not is_subtype(ctx, tmp , Numeric()):
            raise TypeError(f"Can't use unary minus on non-numeric types. Type used: {tmp}")
        return tmp
    
    elif isinstance(node, Return):

        expected = ctx.get_type(RETURN)
        if node.value != None:
            actual = verify(ctx, node.value)
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

        # print("NODE META:", node.meta)

        if ctx.has_var(node.called): # If function is defined

            fd:FuncDef = ctx.get_type(node.called)

            if len(fd.params.args) != len(node.args) :
                raise TypeError(f"Unexpected number of arguments for function {node.called}", meta=node.meta)
            
            for act, exp in zip(node.args, fd.params.args):
                if not is_subtype(ctx, infer_type(ctx,act),  exp.type_):
                    raise TypeError(f"Type mismatch: Expected {exp} but got {act}", meta=node.meta)
    
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