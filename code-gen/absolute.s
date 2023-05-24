	.text
	.file	"absolute.ll"
	.globl	abs                             # -- Begin function abs
	.p2align	4, 0x90
	.type	abs,@function
abs:                                    # @abs
	.cfi_startproc
# %bb.0:                                # %entry
	movq	%rdi, %rax
	testq	%rdi, %rdi
	js	.LBB0_1
# %bb.2:                                # %end_cas_2
	retq
.LBB0_1:                                # %then_cas_2
	negq	%rax
	retq
.Lfunc_end0:
	.size	abs, .Lfunc_end0-abs
	.cfi_endproc
                                        # -- End function
	.section	.rodata.cst16,"aM",@progbits,16
	.p2align	4, 0x0                          # -- Begin function f_abs
.LCPI1_0:
	.quad	0x8000000000000000              # double -0
	.quad	0x8000000000000000              # double -0
	.text
	.globl	f_abs
	.p2align	4, 0x90
	.type	f_abs,@function
f_abs:                                  # @f_abs
	.cfi_startproc
# %bb.0:                                # %entry
	xorpd	%xmm1, %xmm1
	ucomisd	%xmm0, %xmm1
	jbe	.LBB1_2
# %bb.1:                                # %then_cas_5
	xorpd	.LCPI1_0(%rip), %xmm0
.LBB1_2:                                # %end_cas_5
	retq
.Lfunc_end1:
	.size	f_abs, .Lfunc_end1-f_abs
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%r15
	.cfi_def_cfa_offset 16
	pushq	%r14
	.cfi_def_cfa_offset 24
	pushq	%rbx
	.cfi_def_cfa_offset 32
	subq	$16, %rsp
	.cfi_def_cfa_offset 48
	.cfi_offset %rbx, -32
	.cfi_offset %r14, -24
	.cfi_offset %r15, -16
	movsd	c(%rip), %xmm0                  # xmm0 = mem[0],zero
	movl	$.L.str.8, %edi
	movb	$1, %al
	callq	printf@PLT
	movq	absOf@GOTPCREL(%rip), %r15
	movq	(%r15), %rbx
	movq	a(%rip), %r14
	movq	%r14, %rdi
	callq	abs@PLT
	movq	%rbx, %rdi
	movq	%r14, %rsi
	movq	%rax, %rdx
	xorl	%eax, %eax
	callq	printf@PLT
	movq	(%r15), %rbx
	movq	b(%rip), %r14
	movq	%r14, %rdi
	callq	abs@PLT
	movq	%rbx, %rdi
	movq	%r14, %rsi
	movq	%rax, %rdx
	xorl	%eax, %eax
	callq	printf@PLT
	movsd	c(%rip), %xmm0                  # xmm0 = mem[0],zero
	movsd	%xmm0, 8(%rsp)                  # 8-byte Spill
	callq	f_abs@PLT
	movaps	%xmm0, %xmm1
	movl	$.L.str.21, %edi
	movsd	8(%rsp), %xmm0                  # 8-byte Reload
                                        # xmm0 = mem[0],zero
	movb	$2, %al
	callq	printf@PLT
	addq	$16, %rsp
	.cfi_def_cfa_offset 32
	popq	%rbx
	.cfi_def_cfa_offset 24
	popq	%r14
	.cfi_def_cfa_offset 16
	popq	%r15
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	.L.string.cas_1,@object         # @.string.cas_1
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.string.cas_1:
	.asciz	"abs of %d = %d \n"
	.size	.L.string.cas_1, 17

	.type	absOf,@object                   # @absOf
	.data
	.globl	absOf
	.p2align	3, 0x0
absOf:
	.quad	.L.string.cas_1
	.size	absOf, 8

	.type	a,@object                       # @a
	.bss
	.globl	a
	.p2align	3, 0x0
a:
	.quad	0                               # 0x0
	.size	a, 8

	.type	b,@object                       # @b
	.data
	.globl	b
	.p2align	3, 0x0
b:
	.quad	-42                             # 0xffffffffffffffd6
	.size	b, 8

	.type	c,@object                       # @c
	.globl	c
	.p2align	3, 0x0
c:
	.quad	0xc042800000000000              # double -37
	.size	c, 8

	.type	.L.str.8,@object                # @.str.8
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.8:
	.asciz	"c:Double = %f\n"
	.size	.L.str.8, 15

	.type	.L.str.21,@object               # @.str.21
.L.str.21:
	.asciz	"abs of %f.4 = %f.4\n"
	.size	.L.str.21, 20

	.section	".note.GNU-stack","",@progbits
