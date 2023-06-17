

test:Int = 15;
test_b:Int = test+5;

main:Void(){

    a:Int = 0; (* Assignment to 0 is useless or "dead"*)
    a = 10 * test_b * 3; (* This is the only value of a that could be used*)

    b:Int = a + 1; 
    (* However, b it self is not used therefore a isn't 
       used, chaining all the way back to 'test' *)

}