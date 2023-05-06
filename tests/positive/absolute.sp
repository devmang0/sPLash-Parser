
intToStr:String(int:Int){
    (* Since there are no "native" functions to to the cast *)
}

print:Void(s:String){
    (* should print to stdout *)
}

a:Int = 0;

abs:Int where abs >= 0 ( a:Int ){
    if a < 0 {
        return -a;
    }
    return a;
}

main:Void(){

    print( intToStr(abs(12)) );

} 

