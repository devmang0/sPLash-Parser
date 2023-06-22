import json
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Any, Union

from lark  import Lark, ast_utils, Transformer, v_args
from lark.tree import Meta


from dataclasses import dataclass
from typing import List

# As part of trying to make the AST Code more readable as well as
# improving maintainability, we ditch classes that were suposed to native types
# Thus reducing unnecessary locs 




# ====== AST NODES ======

@dataclass
class _Node(ast_utils.Ast):
    pass

@dataclass
class _Ty(ABC):
    pass

    @abstractmethod
    def get_name(self):
        ...

@dataclass
class Array(_Ty, _Node):
    innerType: _Ty

    def get_name(self):
        return "["+self.innerType.get_name()+"]"
    
    def __repr__(self) -> str:
        return "{"+self.get_name()+"}"

@dataclass
class BasicType(_Ty):
    ty_name:str

    def get_name(self):
        return self.ty_name

    def __repr__(self) -> str:
        return f"{{{self.ty_name}}}"

    def __eq__(self, other) -> bool:
        return isinstance(other, BasicType) and self.ty_name == other.ty_name


# "Satic" Instances of Native types
t_int    = BasicType("Int")
t_double = BasicType("Double")
t_string = BasicType("String")
t_bool   = BasicType("Bool" )
t_void   = BasicType("Void")



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
class Comparison(Test):
    l_expr : Expression
    op: str
    r_expr : Expression
    types: tuple = None



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
class FuncCall(Expression, ast_utils.WithMeta):
    meta: Meta
    called: str
    args: List[Expression]
    args_tys: List[_Ty] = None

    def __init__(self, *params):
        self.meta = params[0]
        self.called = params[1]
        self.args = list(params[2:])



@dataclass
class FuncDef(_Statement, ast_utils.WithMeta):
    meta: Meta
    name: str = ""
    type_: str  = "Void"
    refinement: Refinement = None
    params: FuncArgs = None
    block: Block = None    


@dataclass
class FuncDec(_Statement):

    name: str = ""
    type_: str = "Void"
    refinement: Refinement = None
    params: FuncArgs = None


# ==================== BASIC OPERATIONS ====================

# === UNARY === 
@dataclass
class Not(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    expr: Expression

    def __repr__(self) -> str:
        return "Not (!)"

@dataclass
class Neg(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    # op:str
    expr: Expression
    
    def __repr__(self) -> str:
        return "Unary Minus (-)"

# === BINARY ===

@dataclass
class Add(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression
    final_ty: _Ty = None

    def __repr__(self) -> str:
        return "Binary Plus (+)"


@dataclass
class Sub(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression
    final_ty: _Ty = None


    def __repr__(self) -> str:
        return "Binary Minus (+)"

@dataclass
class Mul(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression
    final_ty: _Ty = None


    def __repr__(self) -> str:
        return "Multiplication (*)"

@dataclass
class Div(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression
    final_ty: _Ty = None


    def __repr__(self) -> str:
        return "Division (/)"

@dataclass
class Mod(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression
    final_ty: _Ty = None


    def __repr__(self) -> str:
        return "Modulo (%)"



@dataclass
class And(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

    def __repr__(self) -> str:
        return "And (&&)"



@dataclass
class Or(_Statement, ast_utils.WithMeta):
    
    meta: Meta
    l_expr: Expression
    r_expr: Expression

    def __repr__(self) -> str:
        return "Or (&&)"


@dataclass
class IfThenElse(_Statement, ast_utils.WithMeta):
    meta: Meta
    test: Test
    then_do: Block
    else_do: Block = None

@dataclass
class While(_Statement, ast_utils.WithMeta):
    meta: Meta
    condition: Test
    block: Block

@dataclass
class Return(_Statement, ast_utils.WithMeta):
    meta:Meta
    value: Expression

@dataclass
class Var(_Node):
    name:str
    type_:_Ty = None
    # value:Any


@dataclass
class IndexAccess(_Statement):
    indexed: Var
    index: Any  # Must be checked to be an Int
    final_ty: _Ty = None


@dataclass
class SetVal(_Statement):
    varToSet: Union[Var, IndexAccess]
    value: Expression

    def __init__(self, varToSet, value):
        self.varToSet = varToSet
        self.value = value

@dataclass
class ArrayDef(_Node, ast_utils.WithMeta):
    meta:Meta
    elems:List[Expression]
    final_type: Array

    def __init__(self, meta, *elems):
        self.meta = meta
        self.elems = list(elems)


class toAST(Transformer):

    type_dict = {
        "int" : t_int,
        "double": t_double,
        "bool": t_bool,
        "string": t_string,
        "void": t_void
    }


    
    def NAME(self, n):
        return n.value

    def false(self, b): # BOOL Terminal was not getting parsed correctly
        return Literal(type_=t_bool, val=False)

    def true(self, b): # Same as False
        return Literal(type_=t_bool, val=True)

    def STRING(self, s):
        return Literal(type_=t_string, val=s.value)
    
    def INT(self, i):
        return Literal(type_=t_int, val=int(i.value))
        
    def DOUBLE(self, d):
        return Literal(type_=t_double, val=float(d.value))
    
    def VOID(self, d):
        return Literal(type_=t_void)


    def TYPE(self, t):
        
        if t.value.lower() in self.type_dict:
            return self.type_dict[t.value.lower()]

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
    




# Part of trying to clean up some code, better to embrace
# Too much boilerplate with no actual benefit

# @dataclass
# class Numeric(BasicType):
#     pass

# @dataclass
# class Int(Numeric):
#     pass

# @dataclass
# class Double(Numeric):
#     pass

# @dataclass
# class Bool(BasicType):
#     pass

# @dataclass
# class String(BasicType):
#     pass

# class Void(BasicType):
#     pass
