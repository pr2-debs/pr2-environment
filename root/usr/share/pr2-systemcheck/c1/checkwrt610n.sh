#!/bin/sh

model=`wrt610n -i 10.68.0.5 -p willow model`

if [ "${model}" != "Router model: Linksys WRT610N" ]; then
    echo "Wrong model of wrt610n. ${model}" >&2
    exit 1
fi

exit 0
