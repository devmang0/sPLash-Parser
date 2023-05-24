
class Emitter():

    def __init__(self):
        self.count = 0
        self.lines: list(str) = []
        self.consts = {}
        self.type_tracker = {}
        self.top = -1

        self.ctx = [{}]

    def get_count(self):
        self.count += 1
        return self.count
    
    def get_id(self):
        id = self.get_count()
        return f"cas_{id}"
    
    def __lshift__(self, v):
        self.lines.append(v)

    def __lt__(self, v):
        self.top +=1
        self.lines.insert(self.top, v)

    def get_code(self):
        return "\n".join(self.lines)        
    
    def enter_scope(self):
        print(f"===[SCOPE-{len(self.ctx)}]===")
        self.ctx.append({})
    
    def exit_scope(self):
        self.ctx.pop()
        print(f"===[END-SCOPE-{len(self.ctx)}]===")

    def set_var(self, name, ir_name):
        if name in self.ctx[-1]:
            raise ValueError("Variable already in current context")
        self.ctx[-1][name] = ir_name

    def get_var(self, name):
        for scp in self.ctx.__reversed__():
            if name in scp:
                return scp[name]
        raise ValueError("Variable not in context")

    
    def get_pointer_name(self, n):
        return f"%ptr_{n}"
    
    def set_type(self, name, t):
        self.type_tracker[name] = t

    def get_type(self, name):
        return self.type_tracker[name]
    
    def set_const(self, const, val):
        self.consts[const] = val

    def get_const(self, const):
        return self.consts.get(const, None)
    