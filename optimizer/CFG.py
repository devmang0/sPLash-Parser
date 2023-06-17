from dataclasses import dataclass
from typing import Dict, List, Tuple
from core.splash_ast import *


@dataclass
class BasicBlock():
    statements: list
    dead_code: list

    def __init__(self):
        self.statements=[]
        self.dead_code=[]

    def get_entrypoint(self):
        return self.statements[0]

    def get_exitpoint(self):
        return self.statements[-1]


@dataclass
class Edge():
    
    name: str

    from_block: BasicBlock
    to_block: BasicBlock


class ControlFlowGraph():

    blocks: Dict[int, BasicBlock]
    edges: List[Edge]
    index: int


    def __init__(self):
        self.index = 0
        self.blocks = {}
        self.edges= []

    def insert_edge(self, from_bl:BasicBlock, to_bl:BasicBlock):
        self.edges.append(Edge(from_bl, to_bl))

    def insert_block(self, new_bl:BasicBlock, custom_name:str=None) -> str:
        bl_name = self.index if custom_name == None else custom_name
        self.blocks[bl_name] = new_bl
        self.index += 1
        return bl_name

    def build_from_ast(self, node):
        main = _get_main(node)
        _build_2(self, main)


def _get_main(node:Program) -> FuncDef:
    for st in node.statements:
        if isinstance(st, FuncDef):
            if st.name == "main":
                return st


def _build(cfg: ControlFlowGraph, node, antecedent=None):

    if isinstance(node, FuncDef):
        bl = BasicBlock()
        bl.statements = [_build(cfg, st, antecedent=bl) for st in node.block.statements]
        cfg.insert_block(bl, node.name)

    elif isinstance(node, IfThenElse):
        then_bl = BasicBlock()
        then_bl.statements = [ _build(cfg, st) for st in node.then_do.statements ]
        
        cfg.insert_block(then_bl)
        cfg.insert_edge(antecedent, then_bl)

        if node.else_do != None:
            else_bl = BasicBlock()
            else_bl.statements = [_build(cfg, st) for st in node.then_do.statements]
            cfg.insert_block(else_bl)
            cfg.insert_edge(antecedent, else_bl)

    elif isinstance(node, While):

        whl_bl = BasicBlock()
        whl_bl.statements = [ _build(cfg, st) for st in node.block.statements ]
                
    else:
        return node




def process_block(cfg:ControlFlowGraph, node:Block):
    """
    Due to quirky behaviour from python, this function doesn't have expected output
    
    """
    bl = BasicBlock()
    print("Block id: ", id(bl))

    for st in node.statements:

        is_exit_bl, res = _build_2(cfg, st, bl)
        if is_exit_bl:
            cfg.insert_block(bl)
            bl = res
            print("after reassignment: ", id(bl))
        else:
            bl.statements.append(res)

    cfg.insert_block(bl)
    return bl


def _build_2(cfg:ControlFlowGraph, node, antecedent=None):

    if isinstance(node, FuncDef):
        bl = BasicBlock()
        res = process_block(cfg, node.block)
        print(bl, "||", res)

    
    elif isinstance(node, IfThenElse):

        then_bl = process_block(node, node.then_do)
        cfg.insert_edge(antecedent, then_bl)

        if node.else_do != None:
            else_bl = BasicBlock()
            else_bl.statements = [_build(cfg, st)
                                  for st in node.then_do.statements]
            cfg.insert_block(else_bl)
            cfg.insert_edge(antecedent, else_bl)
    
    else:
        return False, node

