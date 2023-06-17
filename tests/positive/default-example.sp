max:Int (a: Int, b:Int){
    if a > b {
        return a;
    }
    return b;
}

pi:Int = 3; (* Engineers, am i right *)

a:Int = 12345;
b:Int = 54321;
d:Int = 99999;
c:Double = 123.123;

main:Void (){
    print("A: %d\n", a);
    print("B: %d\n", b);

    e:String = "String";
    another:String = "String";

    d:Int = max(a, max(b, d));

    print("MAX IS: %d\n", d);
}