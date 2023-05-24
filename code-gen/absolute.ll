@.string.cas_1 = private unnamed_addr constant [17 x i8] c"abs of %d = %d \0A\00", align 1
@absOf = global ptr @.string.cas_1, align 8
@a = dso_local global i64 0, align 8
@b = dso_local global i64 -42, align 8
@c = dso_local global double -37.0, align 8
@.str.8 = private unnamed_addr constant [15 x i8] c"c:Double = %f\0A\00", align 1
@.str.21 = private unnamed_addr constant [16 x i8] c"abs of %f = %f\0A\00", align 1
declare i32 @printf(i8*, ...) #1
define i64 @abs(i64 %ptr_a){
entry:
    %cas_3 = icmp slt i64 %ptr_a, 0
    br i1 %cas_3, label %then_cas_2, label %end_cas_2
then_cas_2:
%cas_4 = sub i64 0, %ptr_a
        ret i64 %cas_4
end_cas_2:
    ret i64 %ptr_a
}
define double @f_abs(double %ptr_a){
entry:
    %cas_6 = fcmp olt double %ptr_a, 0.0
    br i1 %cas_6, label %then_cas_5, label %end_cas_5
then_cas_5:
%cas_7 = fneg double %ptr_a
        ret double %cas_7
end_cas_5:
    ret double %ptr_a
}
define void @main(){
entry:
    %cas_9 = load double, double* @c, align 8
    %cas_10 = call i32 (i8*, ...) @printf( ptr @.str.8, double %cas_9 )
    %cas_11 = load i8*, i8** @absOf, align 8
    %cas_12 = load i64, i64* @a, align 8
    %cas_13 = load i64, i64* @a, align 8
    %cas_14 = call i64 (i64) @abs( i64 %cas_13 )
    %cas_15 = call i32 (i8*, ...) @printf( i8* %cas_11, i64 %cas_12, i64 %cas_14 )
    %cas_16 = load i8*, i8** @absOf, align 8
    %cas_17 = load i64, i64* @b, align 8
    %cas_18 = load i64, i64* @b, align 8
    %cas_19 = call i64 (i64) @abs( i64 %cas_18 )
    %cas_20 = call i32 (i8*, ...) @printf( i8* %cas_16, i64 %cas_17, i64 %cas_19 )
    %cas_22 = load double, double* @c, align 8
    %cas_23 = load double, double* @c, align 8
    %cas_24 = call double (double) @f_abs( double %cas_23 )
    %cas_25 = call i32 (i8*, ...) @printf( ptr @.str.21, double %cas_22, double %cas_24 )
    ret void
}