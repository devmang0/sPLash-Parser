	.text
	.file	"hello-world.ll"
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rax
	.cfi_def_cfa_offset 16
	movq	greeting@GOTPCREL(%rip), %rax
	movq	(%rax), %rsi
	movl	$.L.str.2, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	popq	%rax
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.type	.L.string.cas_1,@object         # @.string.cas_1
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.string.cas_1:
	.asciz	"Hello"
	.size	.L.string.cas_1, 6

	.type	greeting,@object                # @greeting
	.data
	.globl	greeting
	.p2align	3, 0x0
greeting:
	.quad	.L.string.cas_1
	.size	greeting, 8

	.type	.L.str.2,@object                # @.str.2
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.2:
	.asciz	"%s World!\n"
	.size	.L.str.2, 11

	.section	".note.GNU-stack","",@progbits
