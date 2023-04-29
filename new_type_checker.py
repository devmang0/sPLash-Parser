from dataclasses import dataclass

from typechecking import Context, TypeCheckingError
from splashAST import * 
from splashAST import _Ty, _Node


def handleInt():
    print("TO BE IMPLEMENTED")

@dataclass
class TypeVerifier():

    mapper = {

        Program:handleProgram,
        Int:handleInt,
        FuncDef:handleFunc,
        IfThenElse:handleIfThenElse,
        Comparison:handleComparison,

    }
    

    def __getitem__(self, xs:_Ty):
        return self.mapper.get
    