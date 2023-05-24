@.str.1 = private unnamed_addr constant [12 x i8] c"Hello World\00", align 1
declare i32 @printf(i8*, ...) #1
define void @main(){
entry:
    %cas_2 = call i32 (i8*, ...) @printf( ptr @.str.1 )
    ret void
}