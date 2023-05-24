	.text
	.file	"default-example.ll"
	.globl	max                             # -- Begin function max
	.p2align	4, 0x90
	.type	max,@function
max:                                    # @max
	.cfi_startproc
# %bb.0:                                # %entry
	cmpq	%rsi, %rdi
	jle	.LBB0_2
# %bb.1:                                # %then_cas_1
	movq	%rdi, %rax
	retq
.LBB0_2:                                # %end_cas_1
	movq	%rsi, %rax
	retq
.Lfunc_end0:
	.size	max, .Lfunc_end0-max
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
	movq	a(%rip), %rsi
	movl	$.L.str.3, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	movq	b(%rip), %rsi
	movl	$.L.str.6, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	movq	a(%rip), %rdi
	movq	b(%rip), %rsi
	callq	max@PLT
	movl	$.L.str.9, %edi
	movq	%rax, %rsi
	xorl	%eax, %eax
	callq	printf@PLT
	popq	%rax
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	main, .Lfunc_end1-main
	.cfi_endproc
                                        # -- End function
	.type	pi,@object                      # @pi
	.data
	.globl	pi
	.p2align	3, 0x0
pi:
	.quad	3                               # 0x3
	.size	pi, 8

	.type	a,@object                       # @a
	.globl	a
	.p2align	3, 0x0
a:
	.quad	12345                           # 0x3039
	.size	a, 8

	.type	b,@object                       # @b
	.globl	b
	.p2align	3, 0x0
b:
	.quad	12346                           # 0x303a
	.size	b, 8

	.type	c,@object                       # @c
	.globl	c
	.p2align	3, 0x0
c:
	.quad	0x405ec7df3b645a1d              # double 123.123
	.size	c, 8

	.type	.L.str.3,@object                # @.str.3
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.3:
	.asciz	"A: %d\n"
	.size	.L.str.3, 7

	.type	.L.str.6,@object                # @.str.6
.L.str.6:
	.asciz	"B: %d\n"
	.size	.L.str.6, 7

	.type	.L.str.9,@object                # @.str.9
.L.str.9:
	.asciz	"%d\n"
	.size	.L.str.9, 4

	.section	".note.GNU-stack","",@progbits
