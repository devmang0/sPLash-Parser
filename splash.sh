#!/usr/bin/env bash

flags=""
others=""

for i in $@
do 

    case $i in

        --*) flags="$flags $i";;

        *) others="$others $i";;
    esac

done

python splash_parser.py $flags $others