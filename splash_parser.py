import sys
import os
import argparse
from lark import Lark, Transformer, v_args

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

