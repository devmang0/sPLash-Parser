(* Operation Precedence Test *)

VarDecl:Double;

test:Int = -(2*4 + 6 / 3); (* -10 *)
test2:Double = test*5*127/89.0;

ThisIsAFunction:Void(){}

main:Void(){
    print("%d\n", test);
}