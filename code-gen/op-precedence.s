	.text
	.file	"op-precedence.ll"
	.globl	ThisIsAFunction                 # -- Begin function ThisIsAFunction
	.p2align	4, 0x90
	.type	ThisIsAFunction,@function
ThisIsAFunction:                        # @ThisIsAFunction
	.cfi_startproc
# %bb.0:                                # %entry
	retq
.Lfunc_end0:
	.size	ThisIsAFunction, .Lfunc_end0-ThisIsAFunction
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rax
	.cfi_def_cfa_offset 16
	movq	test(%rip), %rsi
	movl	$.L.str.1, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	popq	%rax
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function
	.type	VarDecl,@object                 # @VarDecl
	.comm	VarDecl,8,8
	.type	test,@object                    # @test
	.data
	.globl	test
	.p2align	3, 0x0
test:
	.quad	-10                             # 0xfffffffffffffff6
	.size	test, 8

	.type	test2,@object                   # @test2
	.globl	test2
	.p2align	3, 0x0
test2:
	.quad	0xc051d64ac9592b25              # double -71.348314606741567
	.size	test2, 8

	.type	.L.str.1,@object                # @.str.1
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.1:
	.asciz	"%d\n"
	.size	.L.str.1, 4

	.section	".note.GNU-stack","",@progbits
