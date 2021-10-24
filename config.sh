#!/bin/bash
export $(grep -v '^#' .env | xargs)
Q='Which project: '
options=("base" "logic" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "base")
            alias dev="python3 ../op/caller.py base"
            break
            ;;
        "logic")
            alias dev="python3 ../op/caller.py logic"
            break
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option";;
    esac
done