import sys

import logging
from lark import Lark, logger

import argparse
import json

from lark import Lark, Transformer, v_args
from lark import ast_utils

from splash_ast import *
from typechecking.context import Context, load_native_functions
from typechecking.typecheck import verify

from compile import compiler


this_module = sys.modules[__name__]


# Dealing with flags and arguments
argparser = argparse.ArgumentParser()
argparser.add_argument("--parsetree", help="print CST pretty", action="store_true")
argparser.add_argument("--rawast", help="Raw AST representation", action="store_true")
argparser.add_argument("--tree", help="AST as json", action="store_true")
argparser.add_argument("--typecheck", help="Typecheck the program", action="store_true")

argparser.add_argument("--llvm", help="outputs llvm file", action="store_true")

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

def test(to_parse: str, currFile:str="example.sp") -> bool:

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
        load_native_functions(ctx)
        verify(ctx, ast)
        # print("typechecks")
    
    if argsp.llvm:
        code_gen = compiler(ast)
        print(code_gen)
        ll_name = currFile.replace(".sp", ".ll")
        with open(file="code-gen/"+ll_name, mode="w+") as f:
            f.write(code_gen)
    
        



def main():
    for file_to_parse in argsp.files:
        with open(file_to_parse) as f:
            file_under_test = file_to_parse.split('/')[-1]
            print(f"Testing: { file_under_test }")
            test(f.read(), file_under_test)


if __name__ == '__main__':
    # print(argsp.files)
    main()

