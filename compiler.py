from splashAST import *


class Emitter(object):

    def __init__(self):
        self.count = 0
        self.lines = []


        def get_count(self):
            self.count += 1
            return self.count
        
        def get_id(self):
            id = self.get_count()
            return f"cas_{id}"
        
        def __lshift__(self, v):
            self.lines.append(v)

        def get_code(self):
            return "\n".join(self.lines)        
        
        def get_pointer_name(self, n):
            return f"%pont_{n}"


def compile(node, emitter=None):

    if isinstance(node, Program):
        emitter = Emitter()
        emitter << "declare i32 @printf(i8*, ...) #1"

        emitter << "define i32 @main() #0 {"

        for stmt in node.statements:
            compile(stmt, emitter)

        emitter << "   ret i32 0"
        emitter << "}"
