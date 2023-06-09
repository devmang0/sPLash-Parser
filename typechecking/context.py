from typing import List, Dict
from dataclasses import dataclass
from core.splash_ast import (
    t_void,
    t_bool,
    t_string,
    t_int,
    t_double,
    Arg,
)

class ContextException(Exception):

    def __init__(self, msg:str):
        super().__init__(msg)


@dataclass
class Context():
    """
        Context for typechecking,
        Makes use of a stack, for every subsequent scope, 
         another dictionary is added to the pile, thus allowing shadowing

    """

    stack = List[Dict]

    def __init__(self):
        self.stack = [{}]

    def get_type(self, name:str):

        for scope in self.stack.__reversed__():
            if name in scope:
                return scope[name]
        raise ContextException(f"Identifier '{name}' not in context")
    


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



def load_native_functions(ctx:Context) -> None:
    ctx.set_type( "print", (t_void, 
                                [Arg(meta=None, 
                                    name="string", 
                                    type_=t_string
                                    )]
                            )
                )
