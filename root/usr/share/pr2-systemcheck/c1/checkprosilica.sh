#!/bin/sh

. /etc/ros/setup.sh

CHECKPROSILICA_PATH=/usr/share/checkprosilica/

${CHECKPROSILICA_PATH}/checkprosilicasettings.py ${CHECKPROSILICA_PATH}/prosilica_attribs.yaml

exit $?
