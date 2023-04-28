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

for i in $others
do
    echo $i
    python splash_parser.py $flags $i
    echo ""
done