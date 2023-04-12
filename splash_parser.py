import sys
import os
import argparse
from dataclasses import dataclass
from typing import List

from lark import Lark, Transformer, v_args
from lark import ast_utils


with open("grammars/sPLash.lark") as _grammar:
    grammar = _grammar.read()


comments = []

_parser = Lark(grammar, parser='lalr', start='start',
               lexer_callbacks={"COMMENT": comments.append})
parse = _parser.parse


argparser = argparse.ArgumentParser()
argparser.add_argument("--tree", help="print AST", action="store_true")
argparser.add_argument("file", help="file to parse")
argsp = argparser.parse_args()


@dataclass
class _ASTNode(ast_utils.Ast):
    pass


class _Statement(_ASTNode):
    pass



@dataclass
class _Program(_ASTNode):
    statements: List[_Statement]




@dataclass
class Declaration(_Statement):
        type_ : str
        name : str 
        refinements : List[Refinement]

@dataclass
class Refinement(_ASTNode):
    refinement: Condition


@dataclass
class Definition(_Statement):
    def __init__(self, name, args, block):
        self.name: name
        self.args = args or []
        self.block = block

class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class Literal:
    def __init__(self, value, type_):
        self.value = value
        self.type_ = type_

class IfThenElse:
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block
        self.else_block = else_block

@dataclass
class While(_Statement):
    condition: Condition
    block: Block

class Return:
    pass



class Block(_ASTNode):
    statements: List[_Statement]



def test(to_parse: str):

    prsd = parse(to_parse)

    if argsp.tree:
        print(prsd.pretty())
        print(comments)

def run_tests():

    with open("./tests/"+argsp.file) as f:
        test(f.read())


if __name__ == '__main__':

    run_tests()

