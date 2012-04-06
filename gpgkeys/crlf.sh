#!/bin/bash
printf "\033[6n" > /dev/tty &
read -sdR -t1 POS
RC=$?
if [ $RC -eq 0 ]; then
    POS="${POS##*\[}"
    ROW="${POS%%;*}"
    COL="${POS##*;}"
    if [ $COL -gt 1 ]; then
        echo
    fi
fi
exit $RC
