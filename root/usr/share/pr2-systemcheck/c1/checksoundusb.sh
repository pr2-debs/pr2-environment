#!/bin/sh

lsusb | grep 046d:0a04 > /dev/null

if [ ! ${?} -eq 0 ]; then
    echo "No Logitech USB speaker found (ID 046d:0a04)" >&2
    exit 2
fi

cat /proc/asound/cards | grep -v "no soundcards" > /dev/null

if [ ! ${?} -eq 0 ]; then
    echo "No soundcards found" >&2
    exit 2
fi

echo "Logitech speaker found and a card is present in /proc/asound/cards"
exit 0
