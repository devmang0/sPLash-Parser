from optimizer.CFG import *
from core.splash_ast import *

class Optimizer():

    ast_root: Program

    def __init__(self, ast):
        cfg = ControlFlowGraph()
        cfg.build_from_ast(ast)
        
        for nm, bl in cfg.blocks.items():
            print(nm, bl)
