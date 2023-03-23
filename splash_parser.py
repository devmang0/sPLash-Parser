#
# This example shows how to write a basic calculator with variables.
#

from lark import Lark, Transformer, v_args


try:
    input = raw_input   # For Python2 compatibility
except NameError:
    pass

with open("grammars/sPLash.lark") as _grammar:
    
    grammar = _grammar.read()


# @v_args(inline=True)    # Affects the signatures of the methods
# class CalculateTree(Transformer):
#     from operator import add, sub, mul, truediv as div, neg
#     number = float

#     def __init__(self):
#         self.vars = {}

#     def assign_var(self, name, value):
#         self.vars[name] = value
#         return value

#     def var(self, name):
#         return self.vars[name]


comments = []

_parser = Lark(grammar, parser='lalr', start='start',lexer_callbacks={"COMMENT": comments.append})
parse = _parser.parse


def main():
    while True:
        try:
            s = input('> ')
        except EOFError:
            break
        print(parse(s))


def test():
    print(parse("""
        (*Comentário muita longo*)\n
        123_1234_124\n
        _1234
                 """).pretty())
    print(comments)
    # print(parse("1+a*-3"))


if __name__ == '__main__':
    test()
    # main()