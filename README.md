# sPLash Compiler (Compilers 22/23)

Parser for sPLash language using LARK.

There are some instructions we need to run in order to ensure the correct functioning of this parser. Namely installing python and virtual env.

If you have python installed, as well as virtual-env feel free to skip the setup steps

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
