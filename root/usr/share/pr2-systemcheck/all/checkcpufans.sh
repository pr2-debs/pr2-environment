#!/bin/sh

IPMITOOL_FILE=`mktemp -t checkipmitoolfan.XXXXXXXXXX`

sudo ipmitool sdr > $IPMITOOL_FILE

count=`grep Fan $IPMITOOL_FILE|wc -l`

res=0

if [ $count != 3 ]; then
    echo "Not all CPU/MB Fans detected. Run \"sudo ipmitool sdr\" to check fans" >&2
    res=1
fi

# Check for 0 RPM in all fans
grep Fan $IPMITOOL_FILE | grep ' 0 RPM'  > /dev/null

if [ ${?} -eq 0 ]; then
    echo "CPU or MB Fans are at 0 RPM. Fan is probably disconnected. Run \"sudo ipmitool sdr\" to check fans" >&2
    res=2
fi

rm $IPMITOOL_FILE

if [ ${res} -eq 0 ]; then
    echo "CPU and MB Fans OK"
fi 

exit ${res}