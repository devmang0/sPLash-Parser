import sys

import logging
from lark import Lark, logger

import argparse
import json

from lark import Lark, Transformer, v_args
from lark import ast_utils

from splash_ast import *
from typechecking.context import Context
from typechecking.typecheck import verify

this_module = sys.modules[__name__]


# Dealing with flags and arguments
argparser = argparse.ArgumentParser()
argparser.add_argument("--parsetree", help="print CST pretty", action="store_true")
argparser.add_argument("--rawast", help="Raw AST representation", action="store_true")
argparser.add_argument("--tree", help="AST as json", action="store_true")
argparser.add_argument("--typecheck", help="Typecheck the program", action="store_true")

argparser.add_argument("files", help="file(s) to parse", nargs='*', default= './positive/hello-world.sp')
argsp = argparser.parse_args()


logger.setLevel(logging.DEBUG)

# Parser

with open("grammars/sPLash.lark") as grammar_file:
    grammar = grammar_file.read()

comments = []

_parser = Lark(grammar, 
               parser='lalr', 
               start='start',
               lexer_callbacks={"COMMENT": comments.append}, keep_all_tokens=False,
               maybe_placeholders=True,
               propagate_positions=True,
               debug=True
               )
parse = _parser.parse


#Transformer

trasformer = ast_utils.create_transformer(this_module, toAST())

## Main execution

def test(to_parse: str) -> bool:

    prsd = parse(to_parse)
    ast = trasformer.transform(prsd)
    if argsp.tree:
        print(json.dumps(ast, indent=4 , cls=jsonAST))
    if argsp.rawast:
        ast = trasformer.transform(prsd)
        print(ast)
        return 
    if argsp.parsetree:
        print(prsd)
        print(prsd.pretty())
        print(comments)

    if argsp.typecheck:
        ctx = Context()
        verify(ctx, ast)
        # print("typechecks")
        return True



def run_tests():
    for file_to_parse in argsp.files:
        with open(file_to_parse) as f:
            print(f"Testing: { file_to_parse.split('/')[-1]}")
            test(f.read())


if __name__ == '__main__':
    # print(argsp.files)
    run_tests()

