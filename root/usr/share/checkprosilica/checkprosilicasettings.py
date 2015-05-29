#!/usr/bin/env python

# Load YAML to dict

# Get attributes

# Check YAML against given attributes

import yaml
import subprocess
import os, sys
import types

FILENAME = 'prosilica_attribs.yaml'
PROSILICA_IP = '10.68.0.20'

def get_my_attribs():
    cmd = 'rosrun prosilica_gige_sdk ListAttributes %s' % PROSILICA_IP

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr = subprocess.PIPE, shell=True)
    o, e = p.communicate()

    if p.returncode != 0:
        print >> sys.stderr, "Unable to get attributes from prosilica. Check connection."
        sys.exit(2)

    attribs = {}
    for ln in o.split('\n'):
        vals = ln.split()

        if len(vals) < 3:
            continue

        if vals[-2] != '=':
            continue

        attribs[vals[0]] = vals[-1]

    if len(attribs.items()) == 0:
        print >> sys.stderr, "Unable to get attributes from prosilica. Check connection."
        sys.exit(2)

    return attribs

def check_running():
    cmd = 'ps ax | grep prosilica_node'
    p = subprocess.Popen(cmd, stdout = subprocess.PIPE, 
                         stderr = subprocess.PIPE, shell = True)

    o, e = p.communicate()

    if len(o.split('\n')) > 3:
        return True
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >> sys.stderr, "No prosilica attributes file given"
        sys.exit(1)

    attribs_file = sys.argv[1]

    if not os.path.exists(attribs_file):
        print >> sys.stderr, "Unable to open file %s. Can't check prosilica" % attribs_file
        sys.exit(2)

    if check_running():
        print >> sys.stderr, "Prosilica camera is running, can't check attribs"        
        sys.exit(254)

    attribs_file = open(attribs_file, 'r')
    good_attribs = yaml.load(attribs_file)

    my_attribs = get_my_attribs()


    result = 0

    for key, val in good_attribs.iteritems():
        if not my_attribs.has_key(key):
            print >> sys.stderr, "Prosilica is missing attribute: %s" % key
            result = 1
            continue

        if type(good_attribs[key]) not in (list, tuple):
            if my_attribs[key] != good_attribs[key]:
                print >> sys.stderr, "Prosilica has incorrect value for %s. Expected %s, got %s" % (key, good_attribs[key], my_attribs[key])
                result = 1
                continue
        else: 
            if my_attribs[key] not in good_attribs[key]:
                print >> sys.stderr, "Prosilica has incorrect value for %s. Expected %s, got %s" % (key, good_attribs[key], my_attribs[key])
                result = 1
                continue


    if result == 0:
        print "Prosilica has correct attributes"
    else:
        print >> sys.stderr, "Prosilica has incorrect attributes. Use \"rosrun prosilica_camera set_inhibition 10.68.0.20\""

    sys.exit(result)

