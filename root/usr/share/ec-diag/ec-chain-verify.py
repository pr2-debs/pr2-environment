#!/usr/bin/python

import yaml
import sys
import getopt
import copy
import subprocess
import tempfile
import os
from sys import stderr

import StringIO
import unittest

portlist = ('p0','p1','p2','p3','J1','J2','J3','J4','J5','J6')

def typename(obj):
    return type(obj).__name__

def asserttype(obj, typename):
    if type(obj).__name__ != typename:
        raise TypeError("expected %s, got %s" %(typename, type(obj).__name__))
    



def is_hub_device(dev):
    if typename(dev) != 'dict':
        return False
    if (not 'product' in dev) or (dev['product'] != 6805014):
        return False
    return True

def is_hub_device_1(dev):
    if not is_hub_device(dev):
        return False;
    if (not 'actuator' in dev) or (dev['actuator'] != 'Hub_J1-J3'):
        return False
    return True

def is_hub_device_2(dev):
    if not is_hub_device(dev):
        return False;
    if (not 'actuator' in dev) or (dev['actuator'] != 'Hub_J4-J6'):
        return False
    return True

def dict_copy_remap(old_dict, new_dict, remap_list):
    asserttype(old_dict, 'dict')
    asserttype(new_dict, 'dict')
    asserttype(remap_list, 'list')
    for key,val in old_dict.iteritems():    
        for remap_item in remap_list:
            asserttype(remap_item, 'tuple')
            (old_key,new_key) = remap_item
            if key == old_key:
                new_dict[new_key] = val

def dict_copy_replace(old_dict, new_dict, replace_dict):
    for key,val in old_dict.iteritems():
        if key in replace_dict:
            new_dict[key] = replace_dict[key]
        else:
            new_dict[key] = old_dict[key]


def merge_hub_ports(dev):
    if typename(dev) != 'dict':
        return dev
    # shallow copy of device
    new_dev = copy.copy(dev)
    # try remaping on all child links of new dev
    for port in portlist:
        if port in new_dev:
            new_dev[port] = merge_hubs_recursive(new_dev[port])
    return new_dev


def match_item_or_list(item_or_list,value):
    """ Allows value to matched against single item or a list of items.
    """
    if not isinstance(item_or_list, list) : item_or_list = [item_or_list]
    return value in item_or_list


def match_serial_and_pcb(h1,h2):
    if (not typename(h1) == 'dict') or (not typename(h2) == 'dict'):
        return False
    if h1.get('serial') != h2.get('serial'):
        return False
    if h1.get('pcb') != h2.get('pcb'):
        return False
    if ('serial' not in h1) or ('pcb' not in h1):
        return False
    return True


def merge_hub_devices(h1,h2):
    if not is_hub_device_1(h1):
        raise TypeError("expected hub1 device")
    if not is_hub_device_2(h2):
        raise TypeError("expected hub2 device")
    new_dev = dict(product=6805014, actuator='Hub', serial=h1['serial'], pcb=h1['pcb'])
    # remap p# of h1 and h2 to J# of new_dict 
    dict_copy_remap(h1, new_dev, [('p0','J1'), ('p1','J2'), ('p2','J3')])
    dict_copy_remap(h2, new_dev, [('p1','J4'), ('p2','J5'), ('p3','J6')])
    # copy all links of dev to new dev 
    return merge_hub_ports(new_dev)

def merge_hubs_recursive(dev):
    # make shallow copies of links
    if is_hub_device_1(dev) and ('p3' in dev) and is_hub_device_2(dev['p3']) :
        h1,h2 = (dev,dev['p3'])
        if match_serial_and_pcb(h1,h2):   
            return merge_hub_devices(h1,h2)
    elif is_hub_device_2(dev) and ('p0' in dev) and is_hub_device_1(dev['p0']) :
        h1,h2 = (dev['p0'],dev)
        if match_serial(h1,h2): 
            return merge_hub_devices(h1,h2)
    # if not part of hub, just recurse ports
    return merge_hub_ports(dev)


def remove_attributes(dev,attrib_list):
    """
    Remove given keys from device map and recuse into child devices
    """
    if (typename(dev) != 'dict'):
        return
    for port in ('p0','p1','p2','p3','J1','J2','J3','J4','J5','J6'):
        if port in dev:
            remove_attributes(dev[port],attrib_list)
    for attrib in attrib_list:
        if attrib in dev:
            del dev[attrib]


def dev2str(dev):
    """
    Produce a description string for a given device
    """
    if dev == None:
        return '*nothing*'
    elif typename(dev) == 'dict':
        if 'actuator' in dev :
            out =  dev['actuator']
        elif 'product' in dev :
            out = 'product=' + dev['product']
        else :
            out = '?'
        if 'note' in dev:
            out += ' (%s)'%dev['note']
        return out
    else :
        return str(dev)


def compare_devs(dev, ideal):
    """
    Compares device attributes.  Device should already be basically the same (devs_match==True), and returns 
    Returns tupple (match,dev_str,ideal_str).  
    If <dev> matches <ideal>,  <match> will be True and <dev_str>, and <ideal_str> will be undefined.
    If <dev> does not match <ideal>, <match> will be False and <dev_str> and <ideal_str> will be description of differences.
    The <dev_str> and <ideal_str> will only containthe attributes that differ between devices.
    """
    asserttype(dev,'dict')
    asserttype(ideal,'dict')
    if not devs_match(dev,ideal):
        raise Exception("compare_devs called with in devices that do not match")
    
    match,dev_str,ideal_str = (True,"","")
    for key,val in ideal.iteritems():
        if (key not in portlist) and (key != 'note'):
            if (key in ['pcb','fw']) and match_item_or_list(ideal.get(key),dev.get(key)) : key_match = True
            else : key_match = (dev.get(key) == ideal.get(key))
            if not key_match:
                match = False
                dev_str   += (" %s=%s"%(key,   dev.get(key) if   dev.get(key)!=None else "*none*"))
                ideal_str += (" %s=%s"%(key, ideal.get(key) if ideal.get(key)!=None else "*none*"))    

    return (match,dev_str,ideal_str)                


def devs_match(dev, ideal):
    """
    Return true if two devices seem similar/the same. Ignores differences like serial# and FW version.
    """
    if typename(dev) != typename(ideal):
        return False
    elif typename(ideal) != 'dict' or typename(dev) != 'dict':
        return ideal == dev
    elif (dev.get('actuator')==None) or (ideal.get('actuator')==None):
        return False
    else:
        return dev.get('actuator') == ideal.get('actuator')


def find_matching_child_device(dev, child, ideal_port):
    """
    Look for matching child device on device.  Look at ideal_port first.
    If child is a device or 'UPLINK' for match on alternate port
    Return matching port or None if nothing is found
    """
    if (ideal_port in dev) and devs_match(dev[ideal_port],child):
        return ideal_port
    elif (typename(child) == 'dict') or (typename(child)=='str' and child=='UPLINK'): 
        # only try to find device on another port if it is a dictioary
        for port in portlist:
            if (port in dev) and devs_match(dev[port],child):
                return port
    return None

def verify_tree_recursive(dev,ideal):
    # this function assumes non-port attributes of dev and ideal already match
    asserttype(dev,'dict')
    asserttype(ideal,'dict')

    msg = ""
    match,dev_str,ideal_str = compare_devs(dev,ideal)
    if not match:
        msg += "  expected : %s\n" % ideal_str
        msg += "  found    : %s\n" % dev_str

    # verify devices connected to ports match 
    dev_port_set = set() 
    dev_port_map = { } # ports mapping between ports on <dev> and ports on <ideal>
    for port in portlist:
        if port in ideal: 
            dev_port = find_matching_child_device(dev, ideal[port], port)
            if dev_port:
                dev_port_set.add(dev_port)
                dev_port_map[dev_port] = port
                if dev_port != port:
                    match = False
                    msg += "  %s : \n" % dev2str(ideal.get(port))
                    msg += "    expected on port : %s\n" % port
                    msg += "    found on port    : %s\n" % dev_port
            else:
                match = False
                dev_port_set.add(port)
                msg += "  On port %s : \n" % port
                msg += "    expected : %s \n" % dev2str(ideal.get(port))
                msg += "    found    : %s \n" % dev2str(dev.get(port))

    # look at all remaining sub-ports on dev
    for port in portlist:
        if (port in dev) and (port not in dev_port_set):
            match = False
            msg += "  On port %s : \n" % port
            msg += "    expected : %s \n" % dev2str(ideal.get(port))
            msg += "    found    : %s \n" % dev2str(dev.get(port))

    if not match:
        msg = "On %s :\n" % dev2str(ideal) + msg
    
    # Follow all devices that do match up.
    for dev_port,ideal_port in dev_port_map.iteritems():
        new_dev,new_ideal = (dev[dev_port],ideal[ideal_port])
        if typename(new_dev) == 'dict' and typename(new_dev) == 'dict':
            match2,msg2 = verify_tree_recursive(new_dev,new_ideal)
            match,msg = (match and match2, msg + msg2)

    return (match, msg)


def verify_tree(dev,ideal):
    """
    Verify <dev> tree to <ideal> tree.  
    <dev> and <ideal> should be dictionary tress created by parsing YAML description of EtherCAT chain.
    If a certain attribute is in <ideal> it should also be present and and match attribute in <dev>.
    If a certain attribute is not in <ideal> dev d/n not need to match it.
    Returns true for match, false for mismatch 
    Outputs description of tree differences to <out>

    Rational:
    Want to be able to make sure device arrangement matches some specified arrangement.  
    However, some device information offset don't matter (such as serial#) and should be ignored. 
    """
    asserttype(dev,'dict')
    asserttype(ideal,'dict')

    # Compare tree(s) of ideal and dict
    if 'tree' not in dev:
        return False, "Input does not contain 'tree' element"

    if 'tree' not in ideal:
        return False, "Ideal Input does not contain 'tree' element"

    dev = dev['tree']
    ideal = ideal['tree']

    if not devs_match(dev,ideal):
        msg = "On master : expected %s, found %s \n" % (dev2str(ideal), dev2str(dev))
        return (False, msg)

    match,msg = verify_tree_recursive(dev,ideal)
    return match, msg
                    
def merge_hubs(dev):
    """
    Merge Hub_J1-J3 and Hub_J4-J6 into single Hub6 element.  
    Input should be YAML representation of EtherCAT tree.  
    Will return another YAML representation of EtherCAT tree.

    Rational:
    WG014 EtherCAT hubs use two EtherCAT slave devices.  
    As such, ec-diag will list hubs as two separate devices.
    However, it it easier to treat hubs as a single 6-port device.
    """
    asserttype(dev,'dict')
    if 'tree' not in dev:
        return dev

    tree = dev['tree']
    new_tree = merge_hubs_recursive(tree)
    if new_tree is tree:
        return dev

    new_dev = {}
    dict_copy_replace(dev,new_dev, {'tree' : new_tree})
    return new_dev


def run_ecdiag(iface):
    fd,filename = tempfile.mkstemp('.yaml','ec-chain')
    #print "Created tmp file %s" % filename
    os.close(fd)

    localpath = os.path.dirname(__file__)
    child = subprocess.Popen([os.path.join(localpath,'ec-diag'), '-i%s'%iface, '-y%s'%filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#    child = subprocess.Popen(['./ec-diag', '-i%s'%iface, '-y%s'%filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = child.communicate()
    if child.returncode == 0:
        fd = open(filename, 'r')
        yaml_in = yaml.load(fd)
        fd.close()
        os.unlink(filename)
        return yaml_in
    else:
        print >> stderr, "Error running ec-diag : "
        print >> stderr, stdoutdata        
        os.unlink(filename)
        sys.exit(1)


class TestInternalFunctions(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_001_match_item_or_list(self):
        self.assertTrue(match_item_or_list(None,None))
        self.assertFalse(match_item_or_list('B.1',None))
        self.assertTrue(match_item_or_list('B.1','B.1'))
        self.assertTrue(match_item_or_list(['B.1','B.2'],'B.2'))
        self.assertFalse(match_item_or_list(['B.1','B.2'],'B.3'))
        self.assertFalse(match_item_or_list(['B.1','B.2'],None))


class TestVerifyFunctions(unittest.TestCase):
    def setUp(self):
        self.tests = []
        testdir = 'verify_tests'
        # load list of test cases from tests folder
        if not os.path.isdir(testdir):
            raise Exception("Can not locate directory  '%s'" % testdir)
        # get list of subdirs in tests
        root,dirs,files = os.walk(testdir).next()
        for dir in dirs:
            if dir == '.svn':
                continue
            devfn = os.path.join(root, dir, 'dev.yaml')
            idealfn = os.path.join(root, dir, 'ideal.yaml')
            outfn = os.path.join(root, dir, 'output.txt')
            #resultfn = os.path.join(root, dir, 'result.yaml')
            if os.path.isfile(devfn) and os.path.isfile(idealfn) and os.path.isfile(outfn):
                self.tests.append( (dir, devfn, idealfn, outfn) )
            else:
                raise Exception("Can not locate test files in %s" % dir)

    def test_verify(self):
        for dir, devfn, idealfn, outfn in self.tests:
            fd = open(devfn,'r')
            dev_yaml = yaml.load(fd)
            fd.close()
            fd = open(idealfn,'r')
            ideal_yaml = yaml.load(fd)
            fd.close()
            match,msg = verify_tree(dev_yaml, ideal_yaml)
            fd = open(outfn)
            msg2 = fd.read()
            fd.close()
            if msg != msg2:
                msg = "Output does not match for %s\nExpected:\n%s\nActual:\n%s\n" % (dir,msg2,msg)
                self.fail(msg)
            self.assertFalse(match)            

    def test_no_change(self):
        # TOOD make sure verify() does not change yaml dictionary tree.        
        1

    def test_equal(self):
        for dir, devfn, idealfn, outfn in self.tests:
            # make sure identical inputs, verify as true
            fd = open(devfn,'r')
            yaml1 = yaml.load(fd)
            fd.close()
            yaml2 = copy.deepcopy(yaml1)
            match,msg = verify_tree(yaml1, yaml2)
            self.assertTrue(match, "Dev tree for %s does not match itself" % dir)

            fd = open(idealfn,'r')
            yaml1 = yaml.load(fd)
            fd.close()
            yaml2 = copy.deepcopy(yaml1)
            match,msg = verify_tree(yaml1, yaml2)
            self.assertTrue(match, "Ideal tree for %s does not match itself" % dir)

    

def runtests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInternalFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVerifyFunctions)
    unittest.TextTestRunner(verbosity=2).run(suite)
    return True



def usage():
    print """
Info:
  Operates on EtherCAT chain descriptions.

Usage :
  ./ec-chain-verify.py [-i <input>] [-r <iface>] [-hmsP] [-v <ideal>] [-o <output>]"
     <yaml_1/2> : YAML formated file containing actual EtherCAT chain
     -h : show this help
     -i : load ECat chain from YAML <input> file. 
     -r : get ECat chain by running ec-diag on interface <iface> 
     -m : merge hubs devices on <input>.
     -s : strip serial numbers from <input>
     -v : Verify <input> ideal against <ideal>.  
          Return zero for match, otherwise non-zero.
          For non-match, outputs differences to stdout.
     -o : Output chain to YAML file. 
     -P : Print chain to stdout. 

Example, create cleaned up version of EtherCAT chain:
  sudo ed-diag -iecat0 -y /tmp/robot.yaml
  ec-chain-verify.py /tmp/robot.yaml -m -s -o ideal-robot.yaml

Example, verify EtherCAT chain against known good chain:
  sudo ec-diag -iecat0 -y /tmp/robot.yaml 
  ec-chain-verify.py /tmp/robot.yaml -m ideal-robot.yaml
"""

def main():
    if len(sys.argv) <= 1:
        usage()
        sys.exit(1)

    optlist,argv = getopt.gnu_getopt(sys.argv, 'hmsv:o:Pi:r:t');

    for opt,arg in optlist:
        if (opt == '-h') :
            usage()
            return 0

    if len(argv) > 1:
        print >>stderr, "Junk arguments : ", " ".join(argv[1:])
        sys.exit(1)

    # all the rest of the options need an input file
    yaml_in = None 

    for opt,arg in optlist:
        if opt in ['-m','-s','-P','-o','-v']:
            if not yaml_in:
                print >>stderr, "Must provide YAML input before using %s" % opt
                sys.exit(1)

        if opt == '-h' :
            usage()
            sys.exit(0)
        elif opt == '-i' : 
            fd = open(arg,'r')
            yaml_in = yaml.load(fd)
            fd.close()
        elif opt == '-r' :
            yaml_in = run_ecdiag(arg)
        elif opt == '-m' : 
            yaml_in = merge_hubs(yaml_in)
        elif opt == '-s' :
            remove_attributes(yaml_in, ['serial'])
        elif opt == '-P' :
            print yaml.dump(yaml_in)
        elif opt == '-o' :
            outfd = open(arg,'w')
            yaml.dump(yaml_in, outfd)
            outfd.close()
        elif opt == '-t' :
            runtests()
            sys.exit(1)
        elif opt == '-v' :
            fd = open(arg,'r')
            yaml_ideal = yaml.load(fd)
            fd.close()
            match,msg = verify_tree(yaml_in, yaml_ideal)
            if match:
                print "Trees match"
                sys.exit(0)
            else:
                print >>stderr, msg
                print "Trees DO NOT match"
                sys.exit(1)
        else :
            print >>stderr, "Internal error : opt = ", opt
            sys.exit(1)

if __name__ == "__main__":
    main()


