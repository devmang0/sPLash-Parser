xs:[Int];

xs[3] = 4; 

len:Int(a:[Int]){
    (*Maybe implement the actual function?*)
}

arrArrARR:[[[Int]]]; (* 3d Arrays *)

sum:Int ( xs:[Int] where len(xs) > 0 ){

    i:Int = 0;
    sum:Int = 0;

    while i < len(xs) {

        sum = sum + xs[counter];

        i = i + 1;
    }

    return sum;

}
(* print(sum(xs)) *)


main:Void(){

    test:Bool = False;

    sum:Int = sum(xs);
    x:[[Int]] = arrArrARR[0];
    y:[Int] = arrArrARR[1][0];

    (*z:Int = test;*)

}