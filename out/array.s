	.text
	.file	"array.ll"
	.globl	len                             # -- Begin function len
	.p2align	4, 0x90
	.type	len,@function
len:                                    # @len
	.cfi_startproc
# %bb.0:                                # %entry
	movl	$5, %eax
	retq
.Lfunc_end0:
	.size	len, .Lfunc_end0-len
	.cfi_endproc
                                        # -- End function
	.globl	sum                             # -- Begin function sum
	.p2align	4, 0x90
	.type	sum,@function
sum:                                    # @sum
	.cfi_startproc
# %bb.0:                                # %entry
	pushq	%rbx
	.cfi_def_cfa_offset 16
	subq	$32, %rsp
	.cfi_def_cfa_offset 48
	.cfi_offset %rbx, -16
	movq	%rdi, %rbx
	movq	$0, 8(%rsp)
	movq	$0, (%rsp)
	movq	$0, 24(%rsp)
	movq	$0, 24(%rdi)
	movq	(%rdi), %rdi
	callq	len@PLT
	movq	%rax, 16(%rsp)
	.p2align	4, 0x90
.LBB1_1:                                # %while_cmp_cas_5
                                        # =>This Inner Loop Header: Depth=1
	movq	8(%rsp), %rax
	cmpq	16(%rsp), %rax
	jge	.LBB1_3
# %bb.2:                                # %while_do_cas_5
                                        #   in Loop: Header=BB1_1 Depth=1
	movq	(%rsp), %rcx
	movq	%rcx, 24(%rsp)
	movq	8(%rsp), %rsi
	movq	(%rbx,%rsi,8), %r8
	addq	%rcx, %r8
	movq	%r8, (%rsp)
	movq	(%rbx,%rsi,8), %rdx
	movl	$.L.str.15, %edi
	xorl	%eax, %eax
	callq	printf@PLT
	incq	8(%rsp)
	jmp	.LBB1_1
.LBB1_3:                                # %while_end_cas_5
	movq	(%rsp), %rax
	addq	$32, %rsp
	.cfi_def_cfa_offset 16
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end1:
	.size	sum, .Lfunc_end1-sum
	.cfi_endproc
                                        # -- End function
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:                                # %entry
	subq	$56, %rsp
	.cfi_def_cfa_offset 64
	movaps	.L.array.cas_30.5+16(%rip), %xmm0
	movaps	%xmm0, 32(%rsp)
	movaps	.L.array.cas_30.5(%rip), %xmm0
	movaps	%xmm0, 16(%rsp)
	movq	$5, 48(%rsp)
	leaq	16(%rsp), %rdi
	movq	%rdi, 8(%rsp)
	callq	sum@PLT
	movq	%rax, (%rsp)
	movl	$.L.str.34, %edi
	movq	%rax, %rsi
	xorl	%eax, %eax
	callq	printf@PLT
	addq	$56, %rsp
	.cfi_def_cfa_offset 8
	retq
.Lfunc_end2:
	.size	main, .Lfunc_end2-main
	.cfi_endproc
                                        # -- End function
	.type	xs,@object                      # @xs
	.comm	xs,8,8
	.type	arrArrARR,@object               # @arrArrARR
	.comm	arrArrARR,8,8
	.type	.L.str.15,@object               # @.str.15
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.15:
	.asciz	"#%d -> el: %d + %d = %d\n"
	.size	.L.str.15, 25

	.type	.L.array.cas_30.5,@object       # @.array.cas_30.5
	.section	.rodata,"a",@progbits
	.p2align	4, 0x0
.L.array.cas_30.5:
	.quad	1                               # 0x1
	.quad	2                               # 0x2
	.quad	3                               # 0x3
	.quad	4                               # 0x4
	.quad	5                               # 0x5
	.size	.L.array.cas_30.5, 40

	.type	.L.str.34,@object               # @.str.34
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str.34:
	.asciz	"SUM: %d\n"
	.size	.L.str.34, 9

	.section	".note.GNU-stack","",@progbits
