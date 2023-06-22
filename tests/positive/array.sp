xs:[Int];

len:Int(a:[Int]){
    return 5;
}

arrArrARR:[[[Int]]]; (* 3d Arrays *)

sum:Int ( xs:[Int] where len(xs) > 0 ){

    i:Int = 0;
    sum:Int = 0;
    before:Int = 0;
    
    max:Int = len(xs);
    while i < max {

        before = sum;
        sum = sum + xs[i];
        print("#%d -> el: %d + %d = %d\n", i, xs[i], before, sum);

        i = i + 1;
    }

    return sum;
}



main:Void(){
    xss:[Int] = {1, 2, 3, 4, 5};
    s:Int = sum(xss);
    print("SUM: %d\n", s);
}