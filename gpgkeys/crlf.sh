#!/bin/bash
echo -en "\033[6n"
read -rsdR POS
POS=${POS##*[}
ROW=${POS%;*}
COL=${POS##*;}
if [ ${COL:-0} -gt 1 ]; then
    echo
fi
