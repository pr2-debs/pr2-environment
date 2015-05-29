#!/bin/sh

. /etc/ros/setup.sh

if ps ax|grep ocean_server|grep -v grep > /dev/null; then
  echo ocean_server running, skipping battery test
  exit 254
fi

BATTERY_ROOT=`rospack find ocean_battery_driver`

if [ -e $BATTERY_ROOT/bin/battery_check ]; then
    rosrun ocean_battery_driver battery_check /etc/ros/sensors/battery0 /etc/ros/sensors/battery1 /etc/ros/sensors/battery2 /etc/ros/sensors/battery3
else
  echo Could not find battery_check in battery_check. Skipping test.
  exit 254
fi

exit ${?}