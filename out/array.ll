@xs = common dso_local global i64* zeroinitializer, align 8
@arrArrARR = common dso_local global i64*** zeroinitializer, align 8
@.str.15 = private unnamed_addr constant [25 x i8] c"#%d -> el: %d + %d = %d\0A\00", align 1
@.array.cas_30.5 = private unnamed_addr constant [5 x i64] [i64 1, i64 2, i64 3, i64 4, i64 5], align 16
@.str.34 = private unnamed_addr constant [9 x i8] c"SUM: %d\0A\00", align 1
declare i32 @printf(i8*, ...) #1
define i64 @len(i64* %ptr_a){
entry:
    ret i64 5
}
define i64 @sum(i64* %ptr_xs){
entry:
    %ptr_i = alloca i64
    store i64 0, i64* %ptr_i, align 8 ; var-def
    %ptr_sum = alloca i64
    store i64 0, i64* %ptr_sum, align 8 ; var-def
    %ptr_before = alloca i64
    store i64 0, i64* %ptr_before, align 8 ; var-def
    %ptr_cas_1 = getelementptr inbounds i64*, i64* %ptr_xs, i64 3
    store i64 0, i64* %ptr_cas_1, align 8
        %cas_3 = load i64*, i64** %ptr_xs, align 4 ; load ptr val
        %cas_4 = call i64 (i64*) @len( i64* %cas_3 )
    %ptr_max = alloca i64
    store i64 %cas_4, i64* %ptr_max, align 8 ; var-def
    br label %while_cmp_cas_5
while_cmp_cas_5:
    %cas_7 = load i64, i64* %ptr_i, align 4 ; load ptr val
    %cas_8 = load i64, i64* %ptr_max, align 4 ; load ptr val
    %cas_6 = icmp slt i64 %cas_7, %cas_8
    br i1 %cas_6, label %while_do_cas_5, label %while_end_cas_5
while_do_cas_5:
        %cas_9 = load i64, i64* %ptr_sum, align 4 ; load ptr val
        store i64 %cas_9, i64* %ptr_before, align 8
        %cas_10 = load i64, i64* %ptr_i, align 4; index-access
        %ptr_cas_11 = getelementptr inbounds i64*, i64* %ptr_xs, i64 %cas_10
        %cas_13 = load i64, i64* %ptr_sum, align 4 ; load ptr val
        %cas_14 = load i64, i64* %ptr_cas_11, align 4 ; load ptr val
        %cas_12 = add  i64 %cas_13, %cas_14
        store i64 %cas_12, i64* %ptr_sum, align 8
        %cas_16 = load i64, i64* %ptr_i, align 4; index-access
        %ptr_cas_17 = getelementptr inbounds i64*, i64* %ptr_xs, i64 %cas_16
        %cas_19 = load i64, i64* %ptr_i, align 4 ; load ptr val
        %cas_21 = load i64, i64* %ptr_cas_17, align 4 ; load ptr val
        %cas_23 = load i64, i64* %ptr_before, align 4 ; load ptr val
        %cas_25 = load i64, i64* %ptr_sum, align 4 ; load ptr val
        %cas_26 = call i32 (i8*, ...) @printf( ptr @.str.15, i64 %cas_19, i64 %cas_21, i64 %cas_23, i64 %cas_25 )
        %cas_28 = load i64, i64* %ptr_i, align 4 ; load ptr val
        %cas_27 = add  i64 %cas_28, 1
        store i64 %cas_27, i64* %ptr_i, align 8
    br label %while_cmp_cas_5
while_end_cas_5:
    %cas_29 = load i64, i64* %ptr_sum, align 4 ; load ptr val
    ret i64 %cas_29
}
define void @main(){
entry:
        %cas_30 = alloca [5 x i64], align 16
        %cas_30_tmp = bitcast [5 x i64]* %cas_30 to i8*
        call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 16 %cas_30_tmp, i8* align 16 bitcast ([5 x i64]* @.array.cas_30.5 to i8*), i64 40, i1 false)
    %ptr_xss = alloca i64*
    store ptr %cas_30, i64** %ptr_xss, align 8 ; var-def
        %cas_32 = load i64*, i64** %ptr_xss, align 4 ; load ptr val
        %cas_33 = call i64 (i64*) @sum( i64* %cas_32 )
    %ptr_s = alloca i64
    store i64 %cas_33, i64* %ptr_s, align 8 ; var-def
    %cas_36 = load i64, i64* %ptr_s, align 4 ; load ptr val
    %cas_37 = call i32 (i8*, ...) @printf( ptr @.str.34, i64 %cas_36 )
    ret void
}
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* noalias nocapture writeonly, i8* noalias nocapture readonly, i64, i1 immarg) #1