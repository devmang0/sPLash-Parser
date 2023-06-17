
absOf:String = "abs of %d = %d \n";


a:Int = 0;
b:Int = -42;

c:Double = -37.0; 

abs:Int where abs >= 0 ( a:Int ){
    if a < 0 {
        return -a;
    }
    return a;
}

f_abs:Double ( a:Double ){
    if a < 0.0 {
        return -a;
    }
    return a;
}

main:Void(){

    print( "c:Double = %f\n", c );

    abs_a:Int = abs(a);
    abs_b:Int = abs(b);
    abs_c:Double = f_abs(c);
    abs_c = 0.0;
    abs_c = f_abs(abs_c) ;

    print( absOf, a, abs_a);
    print( absOf, b, abs_b);
    print( "abs of %f = %f\n", c, abs_c);

} 

