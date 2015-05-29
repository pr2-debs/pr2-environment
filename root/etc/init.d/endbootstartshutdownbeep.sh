#!/bin/sh

if test -e /etc/slave; then
# Slave boot-start
    if (echo $0|grep 'S..startbootbeep.sh' > /dev/null); then
	beep -f 523.25 -l 250 -n -f 587.33 -l 250 -n -f 659.26 -l 250 -n -f 783.99 -l 500
# Slave boot-finish
    elif (echo $0|grep 'S..endbootstartshutdownbeep.sh' > /dev/null); then
	beep -f 659.26 -l 250 -n -f 783.99 -l 250 -n -f 880.00 -l 250 -n -f 1046.50 -l 500
# Slave shutdown-start
    elif (echo $0|grep 'K..endbootstartshutdownbeep.sh' > /dev/null); then
	beep -f 1046.50 -l 250 -n -f 880.00 -l 250 -n -f 783.99 -l 250 -n -f 659.26 -l 500
# Slave shutdown-finish
    elif (echo $0|grep 'S..endshutdownbeep.sh' > /dev/null); then
	beep -f 783.99 -l 250 -n -f 659.26 -l 250 -n -f 587.33 -l 250 -n -f 523.25 -l 500
    fi

else

# Master boot-start
    if (echo $0|grep 'S..startbootbeep.sh' > /dev/null); then
	beep -f 261.63 -l 250 -n -f 293.44 -l 250 -n -f 329.63 -l 250 -n -f 392.00 -l 500
# Master boot-finish
    elif (echo $0|grep 'S..endbootstartshutdownbeep.sh' > /dev/null); then
	beep -f 329.63 -l 250 -n -f 392.00 -l 250 -n -f 440.00 -l 250 -n -f 523.25 -l 500
# Master shutdown-start
    elif (echo $0|grep 'K..endbootstartshutdownbeep.sh' > /dev/null); then
	beep -f 523.25 -l 250 -n -f 440.00 -l 250 -n -f 392.00 -l 250 -n -f 329.63 -l 500
# Master shutdown-finish
    elif (echo $0|grep 'S..endshutdownbeep.sh' > /dev/null); then
	beep -f 392.00 -l 250 -n -f 329.63 -l 250 -n -f 293.44 -l 250 -n -f 261.33 -l 500
    fi

fi




