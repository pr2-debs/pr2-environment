#!/bin/bash

# Checks that all 8 cores of PR2 initialized properly

CORE_COUNT=`mpstat -P ALL|wc -l`

RV=0

# 12 cores is a magic number. If not all cores are detected, then mpstat will not display correct
# number of lines.

if [ $CORE_COUNT != 12 ]; then
    echo "Not all CPU cores detected. Must have 8 CPU cores enabled. Run \"mpstat -P ALL\" for details" >&2
    RV=1
fi

exit ${RV}
