#!/bin/sh

ping -c1 -W1 10.68.0.50 > /dev/null

arp 10.68.0.50 | tail -n1 | grep -v "(incomplete)"

if [ ! ${?} -eq 0 ]; then
    echo "No arp entry for powerboard" >&2 
    exit 1
fi

exit 0