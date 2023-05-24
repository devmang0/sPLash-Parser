@VarDecl = common dso_local global double zeroinitializer, align 8
@test = dso_local global i64 -10, align 8
@test2 = dso_local global double -71.34831460674157, align 8
@.str.1 = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1
declare i32 @printf(i8*, ...) #1
define void @ThisIsAFunction(){
entry:
    ret void
}
define void @main(){
entry:
    %cas_2 = load i64, i64* @test, align 8
    %cas_3 = call i32 (i8*, ...) @printf( ptr @.str.1, i64 %cas_2 )
    ret void
}