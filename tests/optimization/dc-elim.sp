
loop_left:Bool = False;

main:Void(){

    if(False){
        print("This will never get printed");
    }

    a:Int = 0;
    a = 3;

    while( loop_left && (a > 5) ){
        print("Looping: %d\n", loop_left);
        a = a+1;
    }

    a = 5;
    print("Final 'a' value: %d\n", a);

}