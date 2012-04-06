#!/bin/bash
printf "\033[6n" &
read -sdR -t1 POS
rc=$?
if [ $rc -eq 0 ]; then
    POS=${POS##*[}
    ROW=${POS%%;*}
    COL=${POS##*;}
    if [ ${COL:-0} -gt 1 ]; then
        echo
    fi
fi
exit $rc
