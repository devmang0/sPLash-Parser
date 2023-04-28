from dataclasses import dataclass
from splashAST import *
from splashAST import _Ty


RETURN:str = "#RETURN"

@dataclass
class Context():

    stack = [{}]

    def get_type(self, name: str):

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
            raise TypeError(
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

    else:
        print(f"Don't know how to handle {node.__class__.__name__}:{node}")
    