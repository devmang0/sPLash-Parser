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
class Int(Numeric):
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
class Literal():
    type_ : _Ty
    val: any


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


# @dataclass
# class Declaration(_Statement):
#         type_ : BasicType
#         name : str 
#         refinements : List[Refinement] = None

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
class Arg(_Node, ast_utils.WithMeta):
    meta: Meta
    name: str
    type_: _Ty
    refinement: Refinement = None

@dataclass
class VarDef(_Statement, ast_utils.WithMeta):
    meta:Meta
    name:str
    type_:_Ty
    value:Expression

    # @v_args(inline=True)
    # def __init__(self, *args):
    #     print("ARGS: |", args, "|")

@dataclass
class VarDec(_Statement):
    name:str
    type_:_Ty

@dataclass
class IndexAccess(_Statement):
    indexed: Any
    index: Int


@dataclass
class SetVal(_Statement):
    varToSet: Union[str, IndexAccess]
    value: Expression

@dataclass
class FuncCall(Expression, ast_utils.WithMeta):
    meta: Meta
    called: str
    args: List[Expression]

    def __init__(self, *params):
        self.meta = params[0]
        self.called = params[1]
        self.args = list(params[2:])



@dataclass
class FuncDef(_Statement):

    name: str = ""
    type_: str  = "Void"
    refinement: Refinement = None
    params: FuncArgs = None
    block: Block = None    

# ==================== BASIC OPERATIONS ====================

# === UNARY === 
@dataclass
class Not(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    expr: Expression

@dataclass
class Neg(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    # op:str
    expr: Expression

# === BINARY ===

@dataclass
class Add(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression


@dataclass
class Sub(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

@dataclass
class Mul(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

@dataclass
class Div(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression


@dataclass
class Mod(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

@dataclass
class And(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

@dataclass
class Or(_Statement, ast_utils.WithMeta):
    
    meta: Meta
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
class Return(_Statement, ast_utils.WithMeta):
    meta:Meta
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

    def false(self, b):
        # print("BOOL", b)
        return Literal(type_=Bool(), val=False)

    def true(self, b):
        return Literal(type_=Bool(), val=True)

    def STRING(self, s):
        return Literal(type_=String(), val=s[1:-1])
    
    def INT(self, i):
        return Literal(type_=Int(), val=int(i))
        
    def DOUBLE(self, d):
        return Literal(type_=Double(), val=float(d))
    
    def VOID(self, d):
        return Literal(type_=Void())

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
        return { o.__class__.__name__.lower() : { k:v for k, v in o.__dict__.items() if v != None and not isinstance(v, Meta) }}