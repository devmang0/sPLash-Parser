import json
from dataclasses import dataclass
from typing import List, Any

from lark  import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta


from dataclasses import dataclass
from typing import List

t_int = "Int"
t_double = "Double"
t_float = "Float"
t_string = "String"
t_bool = "Bool"
t_void = "Void"



@dataclass
class _Node(ast_utils.Ast):
    pass


@dataclass
class _Ty(_Node):
    pass

@dataclass
class BasicType(_Ty):
    ty: str

@dataclass
class Numeric(_Ty):
    pass

@dataclass
class Int(Numeric):
    pass

@dataclass
class Float(Numeric):
    pass

@dataclass
class _Statement(_Node):
    pass

@dataclass
class Program(_Node, ast_utils.AsList):
    statements: List[_Statement] = None


@dataclass
class Expression(_Statement):
    pass    



@dataclass
class Declaration(_Node):
    pass


@dataclass
class Test(_Node):
    pass


# @dataclass
# class Type(_Node):
#     pass


@dataclass
class Variable(_Node):
    pass

# @dataclass
# class Value(_Node):


@dataclass
class Comparison(_Node):
    l_expr : Expression
    op: str
    r_expr : Expression



@dataclass
class Refinement(_Node):
    cond: Test


@dataclass
class Block(_Node, ast_utils.AsList):
    statements: List[_Statement] = None


@dataclass
class Declaration(_Statement):
        type_ : BasicType
        name : str 
        refinements : List[Refinement] = None

# @dataclass
# class Definition(_Statement):
#         name: str
#         refinement: Refinement
#         # args: Args
#         block: Block

@dataclass
class FuncArgs(_Node, ast_utils.AsList):
    """
        corresponds to func_args
    """
    args: List = None

@dataclass
class Arg(_Node):
    name: str
    type_: BasicType
    refinement: Refinement

@dataclass
class VarDef(_Statement):
    name:str
    type_:str
    value:str

    # @v_args(inline=True)
    # def __init__(self, *args):
    #     print("ARGS: |", args, "|")



@dataclass
class FuncCall(Expression):
    called: str
    args: FuncArgs = None


@dataclass
class FuncDef(_Statement):

    name: str = ""
    type_: str  = "Void"
    refinement: Refinement = None
    args: FuncArgs = None
    block: Block = None    

    # def __init__(self, *args):
    #     print("ARGS: |", args, "|")
        

# @dataclass
# class BinaryOp(_Statement):
#     op:  str
#     left:  Expression
#     right:  Expression


# @dataclass        
# class UnaryOp(_Statement):
#     op: str
#     expr: Expression

# ==================== BASIC OPERATIONS ====================

# === UNARY === 
@dataclass
class Not(_Statement):
    expr: Expression

@dataclass
class Neg(_Statement):
    # op:str
    expr: Expression

# === BINARY ===

@dataclass
class Add(_Statement):
    l_expr: Expression
    r_expr: Expression


@dataclass
class IfThenElse(_Statement):
    test: Test
    then_do: Block
    else_do: Block = None

@dataclass
class While(_Statement):
    # condition: Condition
    block: Block

@dataclass
class Return(_Statement):
    value: Expression

@dataclass
class Var(_Node):
    name:str
    # value:Any



class toAST(Transformer):
    
    def STRING(self, s):
        return s[1:-1]
    
    def INT(self, i):
        return int(i)
        
    def FLOAT(self, f):
        return float(f)

    def TYPE(self, t):
        # print(t)
        if t.value.lower() == t_float.lower():
            return Float()
        

        return BasicType(t.value)

    @v_args(inline=True)
    def start(self, x):
        return x
    


class jsonAST(json.JSONEncoder):
    def default(self, o: Any) -> Any: 

        # Removes fields not collected
        # Removing duplicates fields such as 
        # refinement:{ refinement: {cond:}} could be done, 
        # for representation purposes, but not needed for now
        return { o.__class__.__name__.lower() : { k:v for k, v in o.__dict__.items() if v != None }}