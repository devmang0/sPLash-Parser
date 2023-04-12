from dataclasses import dataclass
from typing import List

from lark  import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta


from dataclasses import dataclass
from typing import List



class _ASTNode(ast_utils.Ast):
    pass

class _Statement(_ASTNode):
    pass

@dataclass
class Program:
    statements: List[_Statement]

@dataclass
class Declaration:
    name: str
    type: str
    refinement: 'Condition' = None

@dataclass
class Definition:
    name: str
    parameters: List['Binder']
    body: 'Block'

@dataclass
class Binder:
    name: str
    type: str
    refinement: 'Condition' = None

@dataclass
class Block:
    statements: List[_Statement]

@dataclass
class IfThenElse:
    condition: 'Condition'
    if_block: 'Block'
    else_block: 'Block' = None

@dataclass
class While:
    condition: 'Condition'
    block: 'Block'

@dataclass
class Return:
    expression: 'Expression' = None

@dataclass
class Add:
    left: 'Expression'
    right: 'Expression'

class toAST(Transformer):
    

    def STRING(self, s):
        return s[1:-1]
    
    def INT(self, i):
        return int(i)
        
    def FLOAT(self, i):


    @v_args(inline=True)
    def start(self, x):
        return x