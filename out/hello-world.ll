@.string.cas_1 = private unnamed_addr constant [6 x i8] c"Hello\00", align 1
@greeting = global ptr @.string.cas_1, align 8
@.str.2 = private unnamed_addr constant [11 x i8] c"%s World!\0A\00", align 1
declare i32 @printf(i8*, ...) #1
define void @main(){
entry:
    %cas_4 = load i8*, i8** @greeting, align 4 ; load ptr val
    %cas_5 = call i32 (i8*, ...) @printf( ptr @.str.2, i8* %cas_4 )
    ret void
}