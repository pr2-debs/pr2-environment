#!/bin/sh

. /etc/ros/setup.sh

# Run Python script to check cameras 
exec /usr/share/checkwge100/checkwge100.py
