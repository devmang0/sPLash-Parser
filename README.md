# sPLash Compiler (Compilers 22/23)

Parser for sPLash language using LARK.

There are some instructions we need to run in order to ensure the correct functioning of this parser. Namely installing python and virtual env.

If you have python installed, as well as virtual-env feel free to skip the setup steps

## LLVM Output and Optimization Process

To tell the compiler to make optimizations, pleas use the `--optimize` flag
To tell the compiler to output the llvm-ir code, please use the `--llvm` flag
To tell the compiler to print the AST, use the `--tree` flag

## Running LLIR Code

> NOTE: This project was made using the most recent version 17 of LLVM Pipeline
> For installation reference: <https://apt.llvm.org>

To run the generated code, please we have to first compile using `llc` and then transform the `.s` file into an executable file using `clang`, for example:

```bash
llc hello-world.ll
clang hello-world.s -o hello-world
# afterwards we can run it as an executable
./hello-world
```

## Setup

I have left a script that will install dependencies, python and the venv package (to avoid global installation). To run the script just use:

```bash
bash setup.sh
```

## Running the parser

After the inital setup, we don't need to run it ever again, just need to activate the venv before using it, which we do so by using:

```bash
source ./venv/bin/activate
```

After this we can really start using the parser, to do so I have also included a script that allows for testing the various examples: 10 positive, and 10 negative.

```bash
# Optionally use tree for AST print-out
# negative tests disregard --tree since no AST is produced
# ./splash [-tree] <file>

./splash --tree positive/hello-world.sp 
./splash negative/hello-worldnt.sp

```

Once done testing the parser, use the command `deactivate` to deactivate the virtual env.

----

## Running compiler

> LLVM Version: 17.0

Basically, just adding the flag `--llvm`, outputs the `.ll` file to `./code-gen/`

Compiles in most recent version of llvm:

```bash
llc array.ll
clang array.s -o array
./array
```

Author: Tomás Algarvio, fc54402
