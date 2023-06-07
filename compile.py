from emitter import Emitter
from typechecking.context import Context
from core.splash_ast import * 
from core.splash_ast import _Ty
from re import findall

# Type translation
tt = {
    "Bool": "i1",
    "String": "i8*",
    "Int": "i64",
    "Double": "double",
    "Void": "void"
}

# Oper Translation
ot = {
    "add_int"   : "add",
    "add_double": "fadd",
    # "Add_string": ""
    "mul_int"   : "mul",
    "mul_double": "fmul",
    "div_int"   : "sdiv",
    "div_float" : "fdiv",
}


get_op = lambda op, tty : ot["_".join(map(str.lower, [op, tty]))]


string_sub = lambda x : {
    "int": "%d",
    "double": "%f",
    "string": "%s"
}[x.lower()]


icmp_ops = {
    "==": "eq",
    "!=": "ne",
    "<" : "slt",
    "<=": "sle",
    ">" : "sgt",
    ">=": "sge",
}

fcmp_ops = {
    "==": "oeq",
    "!=": "one",
    "<":  "olt",
    "<=": "ole",
    ">":  "ogt",
    ">=": "oge",
}

arith_ops = lambda x: {
    "add": "+",
    "sub": "-",
    "mul": "*",
    "div": "/",
    "mod": "%",
    "neg": "-",
}[x.lower()]


type_byte_size = {
    "i1":1,
    "i8*":1,
    "i64":4,
    "double":4,
    "void":0
}

indent = lambda indent:" "*indent*4


def is_agregate_type(ty):
    # for now, only aggregate types will be strings
    if ty == "i8*":
        return True

def to_llir_type(typ: _Ty):
    # print("INSIDE LLIR TYPE:", typ)
    if typ == None:
        return "void"
    return tt[typ.get_name()] if not isinstance(typ, Array) else to_llir_type(typ.innerType)+"*"



def build_static_array(xs:list) -> list:

    if not xs:
        return []

    x = xs[0]

    if isinstance(x, Literal):

        return [f"{to_llir_type(x.type_)} {x.val}"]+build_static_array(xs[1:])

    else:
        return xs



def constant_folding(node:Expression, emt:Emitter):
    """
    Evaluates if expression is a static assignment or not.
    If a static assignment is found, return it's evaluation.
    
    """

    if isinstance(node, (Add, Sub, Mul, Mod, Div)):
        
        lex, l_is_const = constant_folding(node.l_expr, emt)
        rex, r_is_const = constant_folding(node.r_expr, emt)
        
        if l_is_const and r_is_const:
            return eval(f"({str(lex)}) {arith_ops(node.__class__.__name__)} ({str(rex)})"), True
        else:
            return "", False

    elif isinstance(node, Neg):

        ex, is_const = constant_folding(node.expr, emt)
        if is_const:
            return -ex, True

    elif isinstance(node, Literal):
        return node.val, True
    
    elif isinstance(node, Var):
        const = emt.get_const(node.name)
        return const, const!=None
    
    else:
        return "", False


def load_ptr(emt:Emitter, p_name:str, ty:str, i:int=0):
    
    p_tmp = "%"+emt.get_id()
    emt << indent(i)+f"{p_tmp} = load {ty}, {ty}* {p_name}, align 4"
    return p_tmp

def compiler(node, emt:Emitter=None, i=0):
    

    if isinstance(node, Program):
        emt = Emitter()
        emt << "declare i32 @printf(i8*, ...) #1"
        emt.set_type("printf", "i32")
        
        v_defs: list = []
        f_defs: list = []
        remaining: list = []

        for stmt in node.statements:
            # print("COMPILING: ", stmt, "\n\n")
            if isinstance(stmt, (VarDec, FuncDec)):
                compiler(stmt, emt, i)
            elif isinstance(stmt, VarDef):
                v_defs.append(stmt)
            elif isinstance(stmt, (FuncDef)):
                f_defs.append(stmt)

            else:
                remaining.append(stmt)

        for stmt in [*v_defs, *f_defs, *remaining]:
            compiler(stmt, emt, i)

        return emt.get_code()

    elif isinstance(node, FuncDec):
        
        tmp = f"".join([arg for arg in node.params])
        print("FOR FUNCTION:", node.name ," -> ", tmp)
        
        emt < f"declare {f_ty} @{node.name}()"


    elif isinstance(node, FuncDef):
        f_ty = to_llir_type(node.type_)
        emt.set_type(name=node.name, t=f_ty)
        emt.enter_scope()

        emt << f"define {f_ty} @{node.name}({compiler(node.params, emt)}){{"
        emt << "entry:"

        for stmt in node.block.statements:
            compiler(stmt, emt, i+1)

        if f_ty == "void":
            emt << indent(i+1) + "ret void"
        emt << "}"
        emt.exit_scope()

    elif isinstance(node, FuncArgs):

        args = []
        for arg in node.args:
            p_name = emt.get_pointer_name(arg.name)
            p_ty = to_llir_type(arg.type_)
            emt.set_var(arg.name, (p_name, p_ty))
            args.append(p_ty+" "+p_name)
            emt.set_type(p_name, p_ty)

        return ", ".join(args)


    elif isinstance(node, VarDef):

        if i == 0: # Global var
            # print("VARDEF: ", node)
            p_name = f"@{node.name}"
            emt.set_var(node.name, (p_name, "ptr"))
            

            if node.type_ in (t_int, t_double):

                ty = to_llir_type(node.type_)
                const, is_const = constant_folding(node.value, emt)

                if is_const:
                    emt.set_const(node.name, const)
                    const = int(const) if ty == "i64" else float(const)
                    emt < f"{p_name} = dso_local global {ty} {const}, align 8"

                else: 
                    if isinstance(node.value, Neg) and isinstance(node.value.expr, Literal):
                            emt < f"{p_name} = dso_local global {ty} -{node.value.expr.val}, align 8"
                            return
                    ty = to_llir_type(node.type_)

                    # print("INVOKED: ", node.value)
                    val, _ = compiler(node.value, emt, i)
                    emt < f"{p_name} = dso_local global {ty} {val}, align 8"
                    return

            elif node.type_ == t_string:
                const_name = f"@.{node.type_.get_name().lower()}.{emt.get_id()}"
                if isinstance(node.value, Literal):
                    str_size = (len(node.value.val[1:-1]) -
                                len(findall(r'\\.', node.value.val)))+1
                    parse_nl = node.value.val.replace("\\n", "\\0A")[:-1]+'\\00"'
                    emt < f'{const_name} = private unnamed_addr constant [{str_size} x i8] c{parse_nl}, align 1'

                emt < f"{p_name} = global ptr {const_name}, align 8"
            
            else:
                const_name = f"@.{node.type_.get_name()}.{emt.get_id()}"
                e1, t1 = compiler(node.value, emt, i+1)
                reg = const_name+f" = private dso_local unnamed_addr constant c{e1}"
                emt < f"{reg}"
                emt < f"{p_name} = global ptr {const_name}, align 8"

        else:
            
            p_name = emt.get_pointer_name(node.name)
            p_ty = to_llir_type(node.type_) 


            print("VAL_TO_SET:", node.value)
            val, v_ty = compiler(node.value, emt, i+1)
            emt.set_var(node.name, (p_name, "ptr"))
            emt << indent(i)+f"{p_name} = alloca {to_llir_type(node.type_)}"
            emt << indent(i)+f"store {v_ty} {str(val).lower()}, {p_ty}* {p_name}, align {type_byte_size.get(v_ty, '8')} ; var-def"

    elif isinstance(node, VarDec):

        if i == 0: # Global var
            reg = f"@{node.name}"
            ty = to_llir_type(node.type_)
            emt.set_var(node.name, (reg, "ptr"))
            emt < f"{reg} = common dso_local global {ty} zeroinitializer, align 8"


    elif isinstance(node, Return):
        # TODO - how to process return value
        # print("RETURN NODE:", node)
        e, ty = compiler(node.value, emt, 0)
        # ret_ty = t_int
        # print("Return:", e1, ret_ty)

        if isinstance(e, str) and e.startswith("%ptr_"):
            e = load_ptr(emt, e, ty, i)

        emt << indent(i)+f"ret {ty} {e}"

    elif isinstance(node, Literal):


        if node.type_ == t_string:
            str_size = (len(node.val[1:-1]) -
                        len(findall(r'\\.', node.val)))+1
            parse_nl = node.val.replace("\\n", "\\0A")[:-1]+'\\00"'
            reg = f"@.str.{emt.get_count()}"
            emt < f"{reg} = private unnamed_addr constant [{str_size} x i8] c{parse_nl}, align 1"
            emt.set_type(reg, f"[{str_size} x i8]")
            emt.set_var(reg, (reg, "ptr"))
            return (reg, "ptr")

        return (node.val, to_llir_type(node.type_))
    
    elif isinstance(node, FuncCall):
        
        if node.called == "print": 
            node.called = "printf"

        f_ty = compiler(node.called, emt, i)
        f_args = [ compiler(a, emt, i) for a in node.args ]
        f_args_ty = [to_llir_type(f_arg) for f_arg in node.args_tys]


        # print(f"[{node.called}] f_args:   ", f_args)
        # print(f"[{node.called}] typ_check_time:", node.args_tys)
        # print(f"[{node.called}] f_args_ty:", f_args_ty)

        act_args =  []
        for arg, ty in f_args:  # zip(f_args_ty, f_args)

            if ty.startswith("["):
                p_name = f"%{emt.get_id()}"
                emt << indent(i) + f"{p_name} = getelementptr inbounds {ty}, {ty}* {arg}, i64 0, i64 0"
                act_args.append(f"ptr {p_name}")
                continue


            if ty != "ptr":
                p_name = f"%{emt.get_id()}"
                
                emt << indent(
                    i)+f"{p_name} = load {ty}, {ty}* {arg}, align 8"
                act_args.append(f"{ty} {p_name}")
                continue

            act_args.append(f"{ty} {arg}")
            

        f_args_ty_j = ", ".join(f_args_ty) if node.called != "printf" else "i8*, ..."
        f_args_j = ", ".join(act_args)
        reg = f"%{emt.get_id()}"
        emt.set_var(reg, (reg, f_ty))
        emt << indent(i)+f"""{reg} = call {f_ty} ({f_args_ty_j}) @{node.called}( {f_args_j} )"""
        return (reg, f_ty)

    elif isinstance(node, IfThenElse):

        while_id = emt.get_id()
        lbl_then = "then_"+while_id
        lbl_end = "end_"+while_id
        lbl_else = "else_"+while_id

        lbl_next = lbl_end if node.else_do == None else lbl_else

        test, _ = compiler(node.test, emt, i)
        emt << indent(i)+f"br i1 {test}, label %{lbl_then}, label %{lbl_next}"
        emt << f"{lbl_then}:"
        
        emt.enter_scope()
        for st in node.then_do.statements:
            compiler(st, emt, i+1)
        emt.exit_scope()

        if node.else_do != None:
            emt << f"{lbl_else}:"
            
            emt.enter_scope()
            for st in node.else_do.statements:
                compiler(st, emt, i)
            emt.exit_scope()

        emt << f"{lbl_end}:"

    elif isinstance(node, Comparison):

        cond_res = f"%{emt.get_id()}"
        
        lex, l_ty = compiler(node.l_expr, emt, i)
        rex, r_ty = compiler(node.r_expr, emt, i)

        lex = load_ptr(emt, lex, l_ty, i) if not isinstance(
            lex, int) and lex.startswith("%ptr") else lex
        rex = load_ptr(emt, rex, r_ty, i) if not isinstance(rex, int) and rex.startswith("%ptr") else rex

        # Since fcmp only works for floats and icmp only for ints, we must do some work
        l_ty, r_ty = node.types
        cmp_cmd = "fcmp" if l_ty == t_double or r_ty == t_double else "icmp"
        
        # Must cast the int op from int to float
        if cmp_cmd == "fcmp" and not l_ty == r_ty:
            to_cast = lex if l_ty == t_int else rex
            tmp1 = f"%{emt.get_id()}"
            tmp2 = f"%{emt.get_id()}"
            emt << indent(i)+f"{tmp1} = load i64, i64* {to_cast}, align 4"
            emt << indent(i)+f"{tmp2} = sitofp i64 {tmp1} to double"
        
        # Finally we compute the final output type and compare
        ty = "i64" if l_ty==t_int and r_ty==t_int else "double"
        oper = icmp_ops[node.op] if ty == "i64" else fcmp_ops[node.op]
        emt << indent(i)+f"{cond_res} = {cmp_cmd} {oper} {ty} {lex}, {rex}"
        emt.set_var(cond_res, (cond_res, 'i1'))


        
        return cond_res, 'i1'

    elif isinstance(node, (Add, Sub, Mul, Div, Mod)):

        comp_const, is_const = constant_folding(node, emt)
        if is_const:
            ty = to_llir_type(node.final_ty)
            p_name = f"@.{ty}.{emt.get_id()}"
            val = int(comp_const) if ty == "i64" else float(comp_const) 
            emt < f"{p_name} = dso_local global {ty} {val}"

            emt.set_var(p_name, (p_name, "ptr"))

            return p_name, ty
        else:
            lex, l_ty = compiler(node.l_expr, emt, i)
            rex, r_ty = compiler(node.r_expr, emt, i)

            rr = f"%{emt.get_id()}"

            lex = load_ptr(emt, lex, l_ty, i) if not isinstance(lex, int) and lex.startswith("%ptr") else lex
            rex = load_ptr(emt, rex, r_ty, i) if not isinstance(rex, int) and rex.startswith("%ptr") else rex


            # Must cast the int op from int to float
            if l_ty == t_double or r_ty == t_double:
                to_cast = lex if l_ty == t_int else rex
                tmp1 = f"%{emt.get_id()}"
                tmp2 = f"%{emt.get_id()}"
                emt << indent(i)+f"{tmp1} = load i64, i64* {to_cast}, align 4"
                emt << indent(i)+f"{tmp2} = sitofp i64 {tmp1} to double"
                if l_ty == t_int:
                    lex = tmp
                else:
                    rex = tmp

            ty = node.final_ty.get_name().lower()
            if ty == "string":
                # print(f"Trying to concat: {node.l_expr}, {node.r_expr} = {le, re}")
                print(f"IGNORING STRING CONCAT FOR NOW")
                return rr, "i8*"

            oper = get_op(node.__class__.__name__, ty)
            flags = ""

            ty_ = to_llir_type(node.final_ty)

            emt << indent(i)+f"{rr} = {oper} {flags} {ty_} {lex}, {rex}"

            return rr, ty_

    elif isinstance(node, (And, Or)):

        reg = f"%{emt.get_id()}"
        op = node.__class__.__name__.lower()

        lex, lt = compiler(node.l_expr, emt, i)
        rex, rt = compiler(node.r_expr, emt, i)

        emt << f"{reg} = {op} i1 {lex} {rex}"

        return reg, "i1"

    elif isinstance(node, Neg):

        reg = f"%{emt.get_id()}"
        e, t = compiler(node.expr, emt, i)

        if t == "i64": # It's an int
            emt << indent(i)+f"{reg} = sub i64 0, {e}"
        else:
            emt << indent(i)+f"{reg} = fneg double {e}"

        return reg, t 

    elif isinstance(node, Var):

        var, ty = emt.get_var(node.name)
        if ty != "ptr": 
            return var, ty
        # p_name = f"%{emt.get_id()}"

        p_ty = to_llir_type(node.type_)
        # emt << indent(i)+f"{p_name} = load {p_ty}, {p_ty}* {var}, align 8"
        # emt.set_type(p_name, p_ty)
        # emt.set_type(node.name, to_llir_type(node.type_))
        return var, p_ty

    elif isinstance(node, str):
        if node == "print":
            node = "printf"
        return emt.get_type(node)
        
    elif isinstance(node, IndexAccess):

        indexed, indexed_ty = emt.get_var(node.indexed) \
                        if isinstance(node.indexed, str) \
                        else compiler(node.indexed, emt, i)

        index, index_ty = compiler(node.index, emt, i)

        # print(f"[{node.indexed}]Indexed: {indexed} {indexed_ty}")
        print(f"[{node.indexed}]Index: {index} {index_ty}")


        if not isinstance(index, int) and index.startswith("%ptr"):
            ptr_tmp = "%"+emt.get_id()
            emt << indent(i)+f"{ptr_tmp} = load {index_ty}, {index_ty}* {index}, align 4"
            index = ptr_tmp


        p_name = f"{emt.get_pointer_name(emt.get_id())}"
        p_ty = to_llir_type(node.final_ty)
        emt.set_var(p_name, (p_name, p_ty))
        emt << indent(i)+f"{p_name} = getelementptr inbounds {indexed_ty}, {index_ty}* {indexed}, {index_ty} {index}" 

        # reg = f"%{emt.get_id()}"
        # emt << indent(i)+f"{reg} = load {p_ty}, {p_ty}* {p_name}, align {type_byte_size.get(p_ty, 'i8')}"

        return p_name, p_ty


    elif isinstance(node, While):

        while_id = emt.get_id()
        lbl_cmp = "while_cmp_"+while_id
        lbl_do = "while_do_"+while_id
        lbl_end = "while_end_"+while_id
        
        emt << indent(i)+f"br label %{lbl_cmp}"
        emt << f"{lbl_cmp}:"
        test, _ = compiler(node.condition, emt, i)
        emt << indent(i)+f"br i1 {test}, label %{lbl_do}, label %{lbl_end}"
        emt << f"{lbl_do}:"
        
        emt.enter_scope()
        for st in node.block.statements:
            compiler(st, emt, i+1)
        emt.exit_scope()

        emt << indent(i) + f"br label %{lbl_cmp}"

        emt << f"{lbl_end}:"

    elif isinstance(node, SetVal):

        # print("[SET_VAL] ==>", node.value)
        
        var, var_ty = compiler(node.varToSet, emt, i)
        print("[SET_VAL] ==>", node.varToSet, var, var_ty)
        val, val_ty = compiler(node.value, emt, i)

        emt << indent(i)+f"store {val_ty} {val}, {var_ty}* {var}, align 8"

    elif isinstance(node, ArrayDef):

        mempcpy = "@llvm.memcpy.p0i8.p0i8.i64"
        emt.include_decl(mempcpy, f"declare void {mempcpy}(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #1")

        p_name = "%"+emt.get_id()
        const_name = f"@.array.{p_name[1:]}.{len(node.elems)}"
        inner_ty = to_llir_type(node.final_type)
        arr_type = f"[{len(node.elems)} x {inner_ty}]"

        arr_els = build_static_array(node.elems)
        size = len(node.elems) * type_byte_size[inner_ty]

        emt < f"{const_name} = private unnamed_addr constant {arr_type} [{', '.join(arr_els)}], align 16"
        emt << indent(i)+f"{p_name} = alloca {arr_type}, align 16"
        emt << indent(i)+f"{p_name}_tmp = bitcast {arr_type}* {p_name} to i8*"
        emt << indent(i)+f"call void {mempcpy}(i8* align 16 {p_name}_tmp, i8* align 16 bitcast ({arr_type}* {const_name} to i8*), i64 {size}, i1 false)"

        return p_name, arr_type


    else:
        if node == None:
            return "", to_llir_type(t_void) # If 
        print("Can't handle:", node)
        
            
