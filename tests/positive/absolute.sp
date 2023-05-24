
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
    print( absOf, a, abs(a));
    print( absOf, b, abs(b));
    print( "abs of %f = %f\n", c, f_abs(c));

} 

