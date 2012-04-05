#!/bin/bash
echo -en "\033[6n" > /dev/tty
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
