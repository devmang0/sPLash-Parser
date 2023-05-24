from emitter import Emitter
from typechecking.context import Context
from splash_ast import * 
from splash_ast import _Ty
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



def compose_constant(node:Expression, emt:Emitter):
    """
    Evaluates if expression is a static assignment or not.
    If a static assignment is found, return it's evaluation.
    
    """

    if isinstance(node, (Add, Sub, Mul, Mod, Div)):
        
        lex, l_is_const = compose_constant(node.l_expr, emt)
        rex, r_is_const = compose_constant(node.r_expr, emt)
        
        if l_is_const and r_is_const:
            return eval(f"({str(lex)}) {arith_ops(node.__class__.__name__)} ({str(rex)})"), True
        else:
            return "", False

    elif isinstance(node, Neg):

        ex, is_const = compose_constant(node.expr, emt)
        if is_const:
            return -ex, True

    elif isinstance(node, Literal):
        return node.val, True
    
    elif isinstance(node, Var):
        const = emt.get_const(node.name)
        return const, const!=None
    
    else:
        return "", False




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
            elif isinstance(stmt, (VarDef, FuncDef)):
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
            pname = emt.get_pointer_name(arg.name)
            pty = to_llir_type(arg.type_)
            emt.set_var(arg.name, (pname, pty))
            args.append(pty+" "+pname)
            emt.set_type(pname, pty)

        return ", ".join(args)


    elif isinstance(node, VarDef):

        # emt.set_var(node.name, pname)

        if i == 0: # Global var
            # print("VARDEF: ", node)
            pname = f"@{node.name}"
            emt.set_var(node.name, (pname, "ptr"))
            

            if node.type_ in (t_int, t_double):

                ty = to_llir_type(node.type_)
                const, is_const = compose_constant(node.value, emt)

                if is_const:
                    emt.set_const(node.name, const)
                    const = int(const) if ty == "i64" else float(const)
                    emt < f"{pname} = dso_local global {ty} {const}, align 8"

                else: 
                    if isinstance(node.value, Neg) and isinstance(node.value.expr, Literal):
                            emt < f"{pname} = dso_local global {ty} -{node.value.expr.val}, align 8"
                            return
                    ty = to_llir_type(node.type_)

                    print("INVOKED: ", node.value)
                    val, _ = compiler(node.value, emt, i)
                    emt < f"{pname} = dso_local global {ty} {val}, align 8"
                    return

            elif node.type_ == t_string:
                const_name = f"@.{node.type_.get_name().lower()}.{emt.get_id()}"
                if isinstance(node.value, Literal):
                    str_size = (len(node.value.val[1:-1]) -
                                len(findall(r'\\.', node.value.val)))+1
                    parse_nl = node.value.val.replace("\\n", "\\0A")[:-1]+'\\00"'
                    emt < f'{const_name} = private unnamed_addr constant [{str_size} x i8] c{parse_nl}, align 1'

                emt < f"{pname} = global ptr {const_name}, align 8"
            
            else:
                const_name = f"@.{node.type_.get_name()}.{emt.get_id()}"
                e1, t1 = compiler(node.value, emt, i+1)
                reg = const_name+f" = private dso_local unnamed_addr constant c{e1}"
                emt < f"{reg}"
                emt < f"{pname} = global ptr {const_name}, align 8"

        else:
            pname = emt.get_pointer_name(node.name)
            p_ty = to_llir_type(node.type_) 
            emt.set_var(node.name, pname)
            emt << indent(i)+f"{pname} = alloca {to_llir_type(node.type_)}"

    elif isinstance(node, VarDec):

        if i == 0: # Global var
            reg = f"@{node.name}"
            ty = to_llir_type(node.type_)
            emt < f"{reg} = common dso_local global {ty} zeroinitializer, align 8"


    elif isinstance(node, Return):
        # TODO - how to process return value
        print("RETURN NODE:", node)
        e, ty = compiler(node.value, emt, 0)
        # ret_ty = t_int
        # print("Return:", e1, ret_ty)
        emt << indent(i)+f"ret {ty} {e}"

    elif isinstance(node, Literal):


        if node.type_ == t_string:
            # print(f"SIZE of str [{node.val}]:", len(node.val[1:-1]))
            # print(f"What I bet:", len(node.val[1:-1]) - len(findall(r'\\.', node.val)))
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
            # if is_agregate_type(ty):
            #     # Only works for strings
            #     act_args.append(f"{ty} getelementptr inbounds ({ag_ty}, {ag_ty}* {arg}, i64 0, i64 0)")

            # else:
            act_args.append(f"{ty} {arg}")
            

        f_args_ty_j = ", ".join(f_args_ty) if node.called != "printf" else "i8*, ..."
        f_args_j = ", ".join(act_args)
        reg = f"%{emt.get_id()}"
        emt.set_var(reg, (reg, f_ty))
        emt << indent(i)+f"""{reg} = call {f_ty} ({f_args_ty_j}) @{node.called}( {f_args_j} )"""
        return (reg, f_ty)

    elif isinstance(node, IfThenElse):

        if_id = emt.get_id()
        lbl_then = "then_"+if_id
        lbl_end = "end_"+if_id
        lbl_else = "else_"+if_id

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
        lex, _ = compiler(node.l_expr, emt, i)
        rex, _ = compiler(node.r_expr, emt, i)

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
        return (cond_res, 'i1')

    elif isinstance(node, (Add, Sub, Mul, Div, Mod)):

        comp_const, is_const = compose_constant(node, emt)
        if is_const:
            ty = to_llir_type(node.final_ty)
            pname = f"@.{ty}.{emt.get_id()}"
            val = int(comp_const) if ty == "i64" else float(comp_const) 
            emt < f"{pname} = dso_local global {ty} {val}"
            return pname, ty
        else:
            lex, l_ty = compiler(node.l_expr, emt, i)
            rex, r_ty = compiler(node.r_expr, emt, i)

            rr = f"%{emt.get_id()}"


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
                return rr

            oper = get_op(node.__class__.__name__, ty)
            flags = ""

            emt << indent(i)+f"{rr} = {oper} {flags} {ty} {lex} {rex}"

            return rr, ty

    elif isinstance(node, (And, Or)):

        reg = f"%{emt.get_id()}"
        op = node.__class__.__name__.lower()

        print("LEX:", node.l_expr)
        print("REX:", node.r_expr)

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
        emt.set_type(node.name, node.type_)
        var, ty = emt.get_var(node.name)
        if not var.startswith("@"): 
            return (var, ty)
        p_name = f"%{emt.get_id()}"
        p_ty = to_llir_type(node.type_)
        emt << indent(i)+f"{p_name} = load {p_ty}, {p_ty}* {var}, align 8"
        emt.set_type(p_name, p_ty)
        return (p_name, p_ty)

    elif isinstance(node, str):
        if node == "print":
            node = "printf"
        return emt.get_type(node)
        



    else:
        if node == None:
            return "", to_llir_type(t_void) # If 
        print("Can't handle:", node)
        
            
