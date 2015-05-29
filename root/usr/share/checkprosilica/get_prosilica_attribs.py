#!/usr/bin/env python

import sys
import yaml
import subprocess

ignore_attribs = ['CameraName',
                  'DeviceEthAddress',
                  'HostEthAddress',
                  'HostIPAddress',
                  'SerialNumber',
                  'UniqueId',
                  'WhitebalMode',
                  'ExposureMode',
                  'GainMode',
                  'FrameStartTriggerMode',
                  'StreamBytesPerSecond',
                  'Height',
                  'Width',
                  'ExposureValue',
                  'GainValue',
                  'WhitebalValueRed',
                  'WhitebalValueBlue',
                  'RegionX',
                  'RegionY',
                  'PacketSize',
                  'FrameRate',
                  'SyncInLevels',
                  'StatFrameRate',
                  'StatFramesCompleted',
                  'StatFramesDropped',
                  'StatPacketsErroneous',
                  'StatPacketsMissed',
                  'StatPacketsReceived',
                  'StatPacketsRequested',
                  'StatPacketsResent']


def write_attributes(output):
    attribs = {}
    for ln in output.split('\n'):
        vals = ln.split()
        
        if len(vals) < 3:
            continue

        if vals[-2] != '=':
            continue

        if ignore_attribs.count(vals[0]) == 0:
            attribs[vals[0]] = vals[-1]
    
    stream = file('prosilica_attribs.yaml', 'w')
    yaml.dump(attribs, stream)
    


if __name__ == '__main__':
    IP = '10.68.0.20'
    
    cmd = 'rosrun prosilica_gige_sdk ListAttributes %s' % IP
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr = subprocess.PIPE, shell=True)
    o, e = p.communicate()
    
    if p.returncode != 0:
        print >> sys.stderr, "Unable to get Attributes from prosilica"

    write_attributes(o)
