import sys
import os
from lark import Lark, Transformer, v_args

with open("grammars/sPLash_0_2.lark") as _grammar:
    grammar = _grammar.read()


comments = []

_parser = Lark(grammar, parser='lalr', start='start',
               lexer_callbacks={"COMMENT": comments.append})
parse = _parser.parse


def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(parse(s))



def test(to_parse: str):

    prsd = parse(to_parse)

    print(prsd)
    print(prsd.pretty())
    print(comments)
    # print(parse("1+a*-3"))

def run_tests(args):

    
    if len(args) == 1:
        tests = ["default_example.splash"]
    else: 
        tests = [ x for x in os.listdir("./tests") if x.split(".")[0] in args[1:] ]

    for t in tests:

        print("\n Now testing: ", t)
        with open("./tests/"+t) as f:
            test(f.read())
        



        
        



if __name__ == '__main__':
    run_tests(sys.argv)
    # test()
    # main()