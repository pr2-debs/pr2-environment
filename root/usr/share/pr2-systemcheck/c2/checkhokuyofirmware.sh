#!/bin/sh

. /etc/ros/setup.sh

HOKUYO_ROOT=`rospack find hokuyo_node`

check_laser() {
  VERSION=`rosrun hokuyo_node getFirmwareVersion $1 --`
  if [ "$VERSION" = "" ]; then
    echo Unable to get firmware version for $2. >&2
    return 0
  fi
#  if [ "$VERSION" != '1.16.01(16/Nov./2009)' ]; then
  if [ "$VERSION" != '1.18.01(09/Jul./2010)' ] && [ "$VERSION" != '1.16.01(16/Nov./2009)' ]; then
    echo "$2 has wrong version: $VERSION. Expected \"1.16.01(16/Nov./2009)\" or \"1.18.01(09/Jul./2010)\"" >&2
    return 0
  fi
  echo $2 is up to date: $VERSION
  return 1
}

res=0
if ps ax|grep "/hokuyo_node "|grep -v grep > /dev/null; then
  echo hokuyo_node is running. Skipping test.
  exit 254
fi
if [ -e $HOKUYO_ROOT/bin/getFirmwareVersion ]; then
  if check_laser /etc/ros/sensors/base_hokuyo "Base hokuyo"; then
    res=1
  fi
  if check_laser /etc/ros/sensors/tilt_hokuyo "Tilt hokuyo"; then
    res=1
  fi
else
  echo Could not find getFirmwareVersion in hokuyo_node. Skipping test.
  exit 254
fi

exit $res
