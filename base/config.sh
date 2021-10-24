poetry shell
export $(grep -v '^#' ../.env | xargs)
alias dev="python3 ../op/caller.py base"