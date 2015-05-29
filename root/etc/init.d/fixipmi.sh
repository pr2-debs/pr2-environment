#!/bin/sh


target_ip=10.68.0.91
if [ -e /etc/slave ]
then
    target_ip=10.68.0.92
fi

current_static=`sudo ipmitool lan print 1 | sed -nre 's/^IP Address Source\s*: (.*)$/\1/p'`
current_ip=`sudo ipmitool lan print 1 | sed -nre 's/^IP Address\s*: (.*)$/\1/p'`
current_mask=`sudo ipmitool lan print 1 | sed -nre 's/^Subnet Mask\s*: (.*)$/\1/p'`
current_gw=`sudo ipmitool lan print 1 | sed -nre 's/^Default Gateway IP\s*: (.*)$/\1/p'`

if [ "$current_static" != "Static Address" ]
then
    ipmitool lan set 1 ipsrc static
fi

if [ "$current_ip" != "$target_ip" ]
then
    ipmitool lan set 1 ipaddr $target_ip
fi

if [ "$current_mask" != "255.255.255.0" ]
then
    ipmitool lan set 1 netmask 255.255.255.0
fi

if [ "$current_gw" != "10.68.0.1" ]
then
    ipmitool lan set 1 defgw ipaddr 10.68.0.1
fi
