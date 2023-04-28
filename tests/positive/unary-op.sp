
bVal:Bool = False;


(* silly example for testing purposes *)
alwaysTrue:Bool( a:Bool where a!=False ){

    return !a;
}


(* Testing function calls *)
alwaysTrue(bVal);