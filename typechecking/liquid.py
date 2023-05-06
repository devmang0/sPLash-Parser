
# from typechecking import Context
from splash_ast import *


def transformRefinement(op, type_, refinement = None):

    if refinement == None:
        return (type_, refinement)

    if op == Neg:
        # print(f" {{x:{type_}<{refinement}}}")
        pass
    else:
        print("don't know how to transform refinement")


def liquid_type_check(ctx, this, that) -> bool:
    # TODO - implement actual liquid typechecking
    # print(f"This [{json.dumps(this, indent=4, cls=jsonAST)}]")
    # print(f"That [{json.dumps(that, indent=4, cls=jsonAST)}]")
    # raise TypeError("cls")
    return True
