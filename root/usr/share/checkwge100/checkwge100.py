#!/usr/bin/env python

# This is called by a bash script that sources /etc/ros/setup.sh

# Returns "0" if all WGE100 cameras present with correct firmware.

import subprocess
import sys, os

PKG = 'wge100_camera'
try:
    import roslib; roslib.load_manifest(PKG)
except ImportError, e:
    print >> sys.stderr, "Unable to load ROS package \"wge100_camera\". Check \"ROS_PACKAGE_PATH\"."
    sys.exit(1)

class DiscoverException(Exception): pass

FW_VERSION = 'HDL rev: 600 FW rev: 8C41'

CAMERAS = [ 'wide_stereo_l',
            'wide_stereo_r',
            'narrow_stereo_l',
            'narrow_stereo_r',
            'forearm_l',
            'forearm_r' ]

def run_discover():
    """
    @return Discover output
    @rtype str
    """
    cmd = os.path.join(roslib.packages.get_pkg_dir(PKG), 'bin', 'discover')
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    o, e = p.communicate()
    if p.returncode != 0:
        raise DiscoverException("Unable to run discover. Returned code %d." % p.returncode)
    
    return o

def check_camera_firmware(discover, fw_version):
    """
    Returns True if all cameras have correct firmware version
    """
    for ln in discover.split("\n"):
        # Ignore runt lines
        if len(ln) < 10:
            continue

        if ln.find(fw_version) < 0:
            return False

    return True

def get_firmware_version():
    """
    Returns camera FW version as a string
    """
    version_file = os.path.join(roslib.packages.get_pkg_dir(PKG), 'firmware_images', 'version.txt')
    if not os.path.exists(version_file):
        return FW_VERSION

    f = open(version_file, 'r')
    fw_version = f.read()
    f.close()
    
    return fw_version.replace('\n', '')

def find_missing_cameras(discover):
    """
    @rtype [ str ]
    @return Cameras not found by discover
    """
    not_found = []
    for c in CAMERAS:
        if not discover.find('name://' + c) > -1:
            not_found.append(c)

    return not_found

def check_all_cameras():
    fw_version = get_firmware_version()

    not_found = set()

    # Retry three times to make sure we don't have a spurious failure
    for i in range(0, 3):
        try:
            discover = run_discover()
        except Exception, e:
            print >> sys.stderr, "Unable to run \"discover\". Cameras may be missing"
            import traceback
            traceback.print_exc()
            return False

        if not check_camera_firmware(discover, fw_version):
            print >> sys.stderr, "One or more cameras have incorrect firmware. Check that all cameras have FW version \"%s\"." % fw_version
            return False
        
        # A camera is OK if we find it in at least one of our checks
        nf = set(find_missing_cameras(discover))
        if i == 0:
            not_found = nf
        else:
            not_found &= nf

    if not_found:
        print >> sys.stderr, "Unable to find cameras: %s.\nRun \"rosrun wge100_camera discover\" to list all cameras." % ", ".join(not_found)
        return False

    return True

if __name__ == '__main__':
    if not check_all_cameras():
        sys.exit(1)

