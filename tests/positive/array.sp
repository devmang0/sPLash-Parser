xs:[Int];

len:Int(a:[Int]){
    return 5;
}

arrArrARR:[[[Int]]]; (* 3d Arrays *)

sum:Int ( xs:[Int] where len(xs) > 0 ){

    i:Int = 0;
    sum:Int = 0;

    
    max:Int = len(xs);
    while i < max {

        print("#%d -> el: %d => curr sum: %d\n", i, xs[i], sum);
        sum = sum + xs[i];

        i = i + 1;
    }

    return sum;

}
(* print(sum(xs)) *)


main:Void(){
    sum_:Int = sum({1, 2, 3});
    print("SUM: %d\n", sum_);
}