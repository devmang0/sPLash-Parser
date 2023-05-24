	.text
	.file	"cheat.c"
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	movsd	b, %xmm0                        # xmm0 = mem[0],zero
	cvtsi2sdl	a, %xmm1
	divsd	%xmm1, %xmm0
	movsd	%xmm0, b
	movsd	b, %xmm0                        # xmm0 = mem[0],zero
	movabsq	$.L.str, %rdi
	movb	$1, %al
	callq	printf
	xorl	%eax, %eax
	popq	%rbp
	.cfi_def_cfa %rsp, 8
	retq
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.type	b,@object                       # @b
	.data
	.globl	b
	.p2align	3, 0x0
b:
	.quad	0xc060a00000000000              # double -133
	.size	b, 8

	.type	a,@object                       # @a
	.bss
	.globl	a
	.p2align	2, 0x0
a:
	.long	0                               # 0x0
	.size	a, 4

	.type	.L.str,@object                  # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"%f\n"
	.size	.L.str, 4

	.ident	"clang version 10.0.0-4ubuntu1 "
	.section	".note.GNU-stack","",@progbits
