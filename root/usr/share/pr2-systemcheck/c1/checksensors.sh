#!/bin/sh

res=0
for device in imu; do
    if [ -e /etc/ros/sensors/${device} ]; then
	echo "Link for /etc/ros/sensors/${device} is valid"
    else
	echo "Link for /etc/ros/sensors/${device} is invalid" >&2
	res=1
    fi
done

exit ${res}