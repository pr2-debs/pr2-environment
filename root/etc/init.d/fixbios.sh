#!/bin/sh

case "$1" in
start)
	if [ ! -e /etc/slave ]
	then
	    user-nvram -w /usr/lib/pr2-biosopt/C1-BIOS.BIN
	else
	    user-nvram -w /usr/lib/pr2-biosopt/C2-BIOS.BIN
	fi

	;;

stop)
	
	if [ ! -e /etc/slave ]
	then
	    if [ -e /netboot ]
	    then
		rm /netboot
	    else
		user-nvram -w /usr/lib/pr2-biosopt/C1-BIOS-HD.BIN
	    fi
	fi

	;;

*)
	;;

esac
