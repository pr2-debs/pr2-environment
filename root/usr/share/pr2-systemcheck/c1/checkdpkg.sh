#!/bin/sh

if dpkg -l | grep -q '^.U'; then
    echo "dpkg is misconfigured.  Try running: 'dpkg --configure -a' or 'apt-get -f install'" >&2
    exit 1
fi

exit 0