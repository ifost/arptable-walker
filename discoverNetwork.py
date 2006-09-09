#!/usr/bin/env python

import os
import string
import socket
import sys

######################################################################
# SNMP tools wrappers
######################################################################
#
# We assume that we have the UCD snmp agents


os.environ['MIB_DIRS'] = '/usr/share/snmp/mibs:/tmp/snmp'
snmp_cmd_arguments = '-f -m ALL'

usual_prefix = "iso.org.dod.internet.mgmt.mib-2."

def snmpget(host,variable,community=None):
    if community is None: community = 'public'
    cmd = 'snmpget ' + snmp_cmd_arguments + ' ' + host + ' ' + community + ' ' + variable
    return os.popen(cmd + " 2>&1",'r').readlines()

def snmpwalk(host,variable,community=None):
    if community is None: community = 'public'
    cmd = 'snmpwalk ' + snmp_cmd_arguments + ' ' + host + ' ' + community + ' ' + variable
    return os.popen(cmd + " 2>&1",'r').readlines()


######################################################################

ipnetdata='.iso.org.dod.internet.mgmt.mib-2.ip.ipNetToMediaTable.ipNetToMediaEntry.ipNetToMediaNetAddress'


#known_hosts = {'127.0.0.1' : 'localhost'}
known_hosts = {'128.88.36.197' : 'tr1laser'}

def hosts_that_have_contacted_you(target_host,verbose=None):
    if verbose:
        sys.stdout.write(' ['+target_host+'] ')
        sys.stdout.flush()
    snmpinfo = snmpwalk(target_host,ipnetdata)
    ipaddresses = []
    for line in snmpinfo:
        try:
            mibelmt,rhs = string.split(line,'=')
            mibelmt = string.strip(mibelmt)
            parts = string.split(mibelmt,'.')
            splat = string.join(parts[-4:],'.')
            ipaddresses.append(splat)
        except:
            # junk data?? no responses??
            pass
    return ipaddresses



def find_some_more_computers(verbose=None):
    global known_hosts
    newhosts = []
    if verbose:
        sys.stdout.write('Polling: ')
        sys.stdout.flush()
    for host in known_hosts.keys():
        newhosts = hosts_that_have_contacted_you(host,verbose)
        for h in newhosts:
            known_hosts[h] = host  # last reporter of it anyway

def show_known_computers():
    global known_hosts
    keys = known_hosts.keys()
    keys.sort()
    for k in keys:
        try:
            name = socket.gethostbyaddr(k)[0]
        except:
            name = k
        reporter = known_hosts[k]
        print " ",`name`+":",k,"reported by",reporter

while 1:
    print "I know about"
    show_known_computers()
    print
    print "Do you want me to find some more?",
    x = sys.stdin.readline()
    x = string.strip(x)
    if x[0] in 'yY':
        find_some_more_computers(verbose=1)
    elif x[0] in 'nN':
        sys.exit()
    print
    print
    
