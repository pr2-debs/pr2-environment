#!/bin/sh

if ps ax|grep pr2_etherCAT|grep ecat0 > /dev/null; then
  echo pr2_etherCAT running. Skipping test.
  exit 254
fi

if [ `id -u` != 0 ]; then
  echo This test needs to be run as root.
  exit 254
fi

/usr/share/ec-diag/ec-chain-verify.py -r ecat0 -m -v /usr/share/ec-diag/pr2-beta-ecat-chain.yaml
