import json
from dataclasses import dataclass
from typing import List, Any, Union

from lark  import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta


from dataclasses import dataclass
from typing import List

t_int = "Int"
t_double = "Double"
# t_float = "Float"
t_string = "String"
t_bool = "Bool"
t_void = "Void"


# ==== LITERALS ====

@dataclass
class _Literal():
    pass

@dataclass
class IntLit(_Literal):
    val: int = 0

@dataclass
class DoubleLit(_Literal):
    val: float = 0.0

@dataclass
class StringLit(_Literal):
    val: str = ""

@dataclass
class BoolLit(_Literal):
    val: bool = False

@dataclass
class VoidLit(_Literal):
    val: None

# ====== AST NODES ======


@dataclass
class _Node(ast_utils.Ast):
    pass

@dataclass
class _Ty(_Node):
    pass

@dataclass
class Array(_Ty):
    innerType: _Ty

@dataclass
class BasicType(_Ty):
    pass

@dataclass
class Numeric(BasicType):
    pass

@dataclass
class Int(Numeric, IntLit):
    pass

@dataclass
class Double(Numeric):
    pass

@dataclass
class Bool(BasicType):
    pass

@dataclass
class String(BasicType):
    pass

class Void(BasicType):
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



@dataclass
class Variable(_Node):
    pass


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
    type_: _Ty
    refinement: Refinement

@dataclass
class VarDef(_Statement):
    name:str
    type_:_Ty
    value:str

    # @v_args(inline=True)
    # def __init__(self, *args):
    #     print("ARGS: |", args, "|")

@dataclass
class VarDec(_Statement):
    name:str
    type_:_Ty

@dataclass
class IndexAccess(_Statement):
    name: str
    index: Int


@dataclass
class SetVal(_Statement):
    varToSet: Union[str, IndexAccess]
    value: Expression

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
    condition: Test
    block: Block

@dataclass
class Return(_Statement):
    value: Expression

@dataclass
class Var(_Node):
    name:str
    # value:Any



class toAST(Transformer):

    type_dict = {
        "int" : Int,
        "double": Double,
        "float": Double,
        "bool": Bool,
        "string": String,
        "void": Void
    }


    
    def NAME(self, n):
        return n.value

    def BOOL(self, b):
        return BoolLit(bool(b.value.lower()))

    def STRING(self, s):
        return StringLit(s[1:-1])
    
    def INT(self, i):
        return IntLit(int(i))
        
    def DOUBLE(self, d):
        return DoubleLit(float(d))
    
    def VOID(self, d):
        return VoidLit()

    def TYPE(self, t):
        
        if t.value.lower() in self.type_dict:
            return self.type_dict[t.value.lower()]()

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