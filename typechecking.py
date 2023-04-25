from dataclasses import dataclass
from splashAST import *

RETURN="#return"

class TypeError(Exception):
    pass


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
        return name in self.stack[-1][name]


    def enter_scope(self):
        self.stack.append({})

    def exit_scope(self):
        self.stack.pop()




def is_subtype(ctx:Context, this, that ):
    
    return issubclass(this.__class__, that.__class__) and liquid_type_check(ctx, this, that)
         

def infer_type(ctx:Context, name:str):
    pass

def liquid_type_check(ctx:Context, this, that) -> bool:
    print("TO BE IMPLEMENTED")
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
        print(node.block)
        for st in node.block.statements:
            verify(ctx, st)
        ctx.exit_scope()
        ctx.exit_scope()
    elif isinstance(node, IfThenElse):
        if verify(ctx, node.test) != t_bool:
            raise TypeError(f"If Condition: {node.test}, must be a boolean value")
        
        ctx.enter_scope()
        for st in node.else_do.statements:
            verify(ctx, st)
        ctx.exit_scope()
        if node.else_do != None:
            ctx.enter_scope()
            for st in node.else_do.statements:
                verify(ctx, st)
            ctx.exit_scope()
    
    elif isinstance(node, Comparison):
        
        if verify(ctx, node.l_expr) != verify(ctx, node.r_expr):
            raise TypeError(f"""Both operands ({node.l_expr},{node.r_expr}) 
                                must be the same type, later implementations will allow 
                                similar types to be compared e.g: (Float, Number)""")
        
        return True

    elif isinstance(node, Var):
        if not ctx.has_var(node.name):
            raise TypeError(f"Variable {node.name} not defined in current context")
        return ctx.get_type(node.name)
    
    elif isinstance(node, VarDef):
        if ctx.is_var_in_current_scope(node.name):
            raise TypeError(f"Variable {node.name} already defined in current context")
    

    
    elif isinstance(node, float):
        return t_float
        


    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")