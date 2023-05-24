@pi = dso_local global i64 3, align 8
@a = dso_local global i64 12345, align 8
@b = dso_local global i64 12346, align 8
@c = dso_local global double 123.123, align 8
@.str.3 = private unnamed_addr constant [7 x i8] c"A: %d\0A\00", align 1
@.str.6 = private unnamed_addr constant [7 x i8] c"B: %d\0A\00", align 1
@.str.9 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
declare i32 @printf(i8*, ...) #1
define i64 @max(i64 %ptr_a, i64 %ptr_b){
entry:
    %cas_2 = icmp sgt i64 %ptr_a, %ptr_b
    br i1 %cas_2, label %then_cas_1, label %end_cas_1
then_cas_1:
        ret i64 %ptr_a
end_cas_1:
    ret i64 %ptr_b
}
define void @main(){
entry:
    %cas_4 = load i64, i64* @a, align 8
    %cas_5 = call i32 (i8*, ...) @printf( ptr @.str.3, i64 %cas_4 )
    %cas_7 = load i64, i64* @b, align 8
    %cas_8 = call i32 (i8*, ...) @printf( ptr @.str.6, i64 %cas_7 )
    %cas_10 = load i64, i64* @a, align 8
    %cas_11 = load i64, i64* @b, align 8
    %cas_12 = call i64 (i64, i64) @max( i64 %cas_10, i64 %cas_11 )
    %cas_13 = call i32 (i8*, ...) @printf( ptr @.str.9, i64 %cas_12 )
    ret void
}