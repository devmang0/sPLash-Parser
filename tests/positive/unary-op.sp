
bVal:Bool = false;


(* silly example for testing purposes *)
alwaysTrue:Bool( a:Bool where a!=false ){

    return !a;
}


(* Testing function calls *)
alwaysTrue(bVal);