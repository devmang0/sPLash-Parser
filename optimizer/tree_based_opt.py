from dataclasses import dataclass
from typing import Dict, List, Any

from core.splash_ast import *
from core.splash_ast import _Node


def arith_ops(x): return {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "div": "/",
    "mod": "%",
    "neg": "-",
}[x.lower()]

@dataclass
class Variable():
    
    name:str
    is_const:bool
    val:Any


    defs_not_used:List
    last_def_used: bool

    def __init__(self, name, is_const, val):
        self.name = name
        self.is_const = is_const
        self.val = val
        self.defs_not_used = []
        self.last_def_used = True


    def mark_def(self, def_node):
        """
        Returns whether or not node is dead
        """

        if not self.last_def_used:
            old_def, was_used = self.defs_not_used[-1]
            if isinstance(def_node,	 SetVal):
                old_def.value = def_node.value
                was_used = False
                return True
            
                
        self.defs_not_used.append([def_node, False])
        self.last_def_used = False
        return False
        

    def mark_use(self):
        self.last_def_used = True
        self.defs_not_used[-1][1] = True 

    def collect_dead(self):
        return [ node for node, is_alive in self.defs_not_used if not is_alive ]


class TreeBasedOptimizer():

    var_list: List[Variable]
    var_ctxs: List[ Dict[str, Variable] ]
    dead_code_nodes: List[_Node]

    flatten_blocks: list

    def __init__(self):
        self.var_ctxs = [{}]
        self.var_list = []
        self.dead_code_nodes = []
        self.flatten_blocks=[]

    def insert_var(self, var:Variable):
        self.var_list.append(var)
        self.var_ctxs[-1][var.name] = var

    def get_var(self, name) -> Variable:
        for ctx in self.var_ctxs.__reversed__():
            if name in ctx:
                return ctx[name]
        raise ValueError(f"Var {name} not present in context")


    def mark_dead_code(self, node:_Node):
        self.dead_code_nodes.append(node)

    def enter_scope(self):
        self.var_ctxs.append({})
    
    def exit_scope(self):
        self.var_ctxs.pop()

    def eval_test(self, test):
        """
            Evaluates if it always evals to the same
        """

        return True, test


def pass_(tbo:TreeBasedOptimizer, node, i=1):


    if isinstance(node, Program):

        # print(f" === PASS #{i} ===")

        v_defs: list = []
        f_defs: list = []
        remaining: list = []

        for st in node.statements:
            if isinstance(st, (VarDec, FuncDec)):
                pass_(tbo, st)
            elif isinstance(st, VarDef):
                v_defs.append(st)
            elif isinstance(st, (FuncDef)):
                f_defs.append(st)
            else:
                remaining.append(st)

        for st in [*v_defs, *f_defs, *remaining]:
            pass_(tbo, st)
            
        for var in tbo.var_list:
            tbo.dead_code_nodes += var.collect_dead()

        if i != 1:
            node = rebuild_ast(tbo, node)
            tbo.var_list = []
            pass_(tbo, node, i-1)
                

    elif isinstance(node, VarDef):

        # === === FOLD & PROPAGATION CONST's === ===
        is_const, val = _fold_propagate(tbo, node.value)

        v = Variable(node.name, is_const, val)
        tbo.insert_var(v)

        if is_const:
            node.value = Literal(node.type_, val)

        v.mark_def(node)

    elif isinstance(node, SetVal):

        # === === FOLD & PROPAGATION CONST's  === ===
        is_const, val = _fold_propagate(tbo, node.value)
        
        var_name = node.varToSet.name \
                    if isinstance(node.varToSet, Var) \
                    else node.varToSet.indexed.name
                
        fetched = tbo.get_var(var_name)
        fetched.is_const = is_const
        fetched.val = val
        
        if is_const:
            var_type = node.varToSet.type_ \
                if isinstance(node.varToSet, Var) \
                else node.varToSet.final_ty
            node.value = Literal(var_type, val)
    
        if fetched.mark_def(node): # Part of dead assignment removal
            tbo.dead_code_nodes.append(node)
        
    elif isinstance(node, FuncDef):

        tbo.enter_scope()
        for param in node.params.args:
            v = Variable(param.name, False, None)
            v.mark_def(param)
            tbo.insert_var(v)
        tbo.enter_scope()
        for st in node.block.statements:
            pass_(tbo, st)
        
        tbo.exit_scope()
        tbo.exit_scope()
    
    elif isinstance(node, FuncCall):
        
        for arg in node.args:
            pass_(tbo, arg)

    elif isinstance(node, Var):
        v = tbo.get_var(node.name)
        v.mark_use()

    elif isinstance(node, IfThenElse):
        
        is_const, test = _fold_propagate(tbo, node.test)
        
        if is_const and test: # always enters if
             
            tbo.flatten_blocks.append( (node, node.then_do) )

        elif is_const and not test: # never enters if
            
            if node.else_do == None:
                tbo.dead_code_nodes.append(node)
                return 

            tbo.flatten_blocks.append( (node, node.else_do) )

    elif isinstance(node, While):

        is_const, test = _fold_propagate(tbo, node.condition)
        
        if is_const and not test:
            tbo.dead_code_nodes.append(node)

    elif isinstance(node, (Literal, Neg, Add, Sub, Mul, Mod, Div)):

        return _fold_propagate(tbo, node)
    
    else: 
        return node



def _fold_propagate(tbo:TreeBasedOptimizer, node):

    if isinstance(node, Literal):
        return True, node.val
    
    elif isinstance(node, Var):

        var = tbo.get_var(node.name)
        var.mark_use()
        return var.is_const, var.val

    elif isinstance(node, Neg):

        is_const, expr = _fold_propagate(tbo, node.expr)

        return is_const, -expr
    
    elif isinstance(node, (Add, Sub, Mul, Mod, Div)):

        l_is_const, l_val = _fold_propagate(tbo, node.l_expr)
        r_is_const, r_val = _fold_propagate(tbo, node.r_expr)

        if l_is_const and r_is_const:
            return True, eval(f"({str(l_val)}) {arith_ops(node.__class__.__name__)} ({str(r_val)})")
        else:
            return False, None
    
    elif isinstance(node, (And, Or)):

        l_is_const, l_val = _fold_propagate(tbo, node.l_expr)
        r_is_const, r_val = _fold_propagate(tbo, node.r_expr)

        if l_is_const and r_is_const:
            return True, eval(f"({str(l_val)} {(node.__class__.__name__.lower())} {str(r_val)})")
        else:
            return False, None
    
    elif isinstance(node, (Not)):

        is_const, expr = _fold_propagate(tbo, node.expr)

        return is_const, not expr

    elif isinstance(node, Comparison):

        l_is_const, l_val = _fold_propagate(tbo, node.l_expr)
        r_is_const, r_val = _fold_propagate(tbo, node.r_expr)

        if l_is_const and r_is_const:
            return True, eval(f"({str(l_val)} {(node.op)} {str(r_val)})")
        else:
            return False, None
        
    elif isinstance(node, FuncCall):

        for arg in node.args:
            _fold_propagate(tbo, arg)

        return False, node

    else:
        print("Can't fold ", node)
        return False, node




def rebuild_ast(tbo:TreeBasedOptimizer, node, predecessor=None, insert_at=0 ):
    """
        Rebuilds the ast, removing dead nodes
    """

    if node in tbo.dead_code_nodes:
        return False, None # Returns False because it's not a node
    
    if node in [ nd for nd, _ in tbo.flatten_blocks ]:

        nd, blk = [(nd, blk) for nd, blk in tbo.flatten_blocks if nd == node][0]
        

        for i, st in enumerate(blk.statements):
            predecessor.insert(insert_at+i, st)
        
        predecessor.remove(node) # Remove block that's going to be flattened
        return False, None

    elif isinstance(node, Program): 
        
        prog = Program()
        prog.statements = []

        for i, st in enumerate(node.statements): # Potential one line but harder to read :)
            is_node, nd = rebuild_ast(tbo, st, node.statements, i+1)
            if is_node:
                prog.statements.append(nd)

        return prog
        
    elif isinstance(node, FuncDef):

        fdef = FuncDef(node.meta, node.name, node.type_, node.refinement, node.params, Block())
        fdef.block.statements = []
        
        for i, st in enumerate(node.block.statements):
            is_node, nd = rebuild_ast(tbo, st, node.block.statements, i)
            if is_node:
                fdef.block.statements.append(nd)

        return True, fdef

    elif isinstance(node, IfThenElse):

        is_static, test = tbo.eval_test(node.test)

        ifelse = IfThenElse(node.meta, test, Block(), Block() if node.else_do != None else None)

        ifelse.then_do.statements = []
        for i, st in enumerate(node.then_do.statements):
            is_node, nd = rebuild_ast(tbo, st, node.then_do.statements, i+1)
            if is_node:
                ifelse.then_do.statements.append(nd)
        
        if node.else_do != None:
            ifelse.else_do.statements = []
            for i, st in enumerate(node.else_do.statements):
                is_node, nd = rebuild_ast(tbo, st, node.else_do.statements, i+1)
                if is_node:
                    ifelse.else_do.statements.append(nd)

        return True, ifelse

    elif isinstance(node, While):

        is_static, test = tbo.eval_test(node.condition)

        whl = While(node.meta, test, Block())
        whl.block.statements = []
        for i, st in enumerate(node.block.statements):
            is_node, nd = rebuild_ast(tbo, st, node.block.statements, i+1)
            if is_node:
                whl.block.statements.append(nd)

        return True, whl

    else:
        return True, node


