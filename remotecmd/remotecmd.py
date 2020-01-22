#!/usr/bin/python27

"""
Monitoring alert to verify if a Blaze process is running and properly registered on gosredirector.
"""
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Date: March, 2017

import sys
import socket
import struct
import urllib3
import xmltodict
import os, subprocess
from pprint import pprint
from pssh import ParallelSSHClient
from netaddr import *
from lxml import etree
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
from optparse import OptionParser

servicename = ''
ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}


def allkeys(k2b,o):
  if isinstance(o, dict):
    for k, v in o.iteritems():
      if k == k2b and not hasattr(v, '__iter__'): yield v
      else:
        for r in  allkeys(k2b,v): yield r
  elif hasattr(o, '__iter__'):
    for r in [ allkeys(k2b,i) for i in o ]:
      for r2 in r: yield r2
  return


def get_all_leaf_nodes(data):
    """
    Make a recursive search in the directory received
    """
    class Namespace(object):
        pass
    ns = Namespace()
    ns.results = []
    def inner(data):
        if isinstance(data, dict):
            for item in data.values():
                inner(item)
        elif isinstance(data, list) or isinstance(data, tuple):
            for item in data:
                inner(item)
        else:
            ns.results.append(data)
    inner(data)
    return ns.results

def bashcommand(hostdomains, command):
    
    client = ParallelSSHClient(hostdomains)
    output = client.run_command(command)
    for hos in output:
        for line in output[hos].stdout:
            pprint ("Host %s : %s'" % (hos, line))   


def searchinchredirector(searchurl, servicename, command):
    """
    Searching and getting the xml of redirector.
    """
    servicenamefound = {}
    allservicenamesfound = []
    hostsipv4 = []
    hostdomains = []
    http = urllib3.PoolManager(retries=False)

    try:
        reqredirectorurl = http.request('GET', searchurl, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_UNK, 'Failed to get the redirector xml', "")

    xmlredir = xmltodict.parse(reqredirectorurl.data)
    if len(reqredirectorurl.data) < 100:
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information \
                                 associated with it", "")

    root = etree.fromstring(reqredirectorurl.data)
    [allservicenamesfound.append(sname.text) for sname in root.iter("name")]
    for tag in range(len(allservicenamesfound)):
        if len(allservicenamesfound) > 1:
            if servicename == xmlredir['serverlist']['servers']['serverinfodata'][tag]['name']:
                servicenamefound = xmlredir['serverlist']['servers']['serverinfodata'][tag]
        else:
            if servicename == xmlredir['serverlist']['servers']['serverinfodata']['name']:
                servicenamefound = xmlredir['serverlist']['servers']['serverinfodata']

    if not (servicename in get_all_leaf_nodes(servicenamefound)):
        plugin_exit(STATUS_CRIT, "Servicename not registered on Redirector", "")
    else:
         pass

    hostnamesm =  [x for x in allkeys('ip', servicenamefound['masterinstance'])]
    hostsnamesmshort = list(set([y for y in hostnamesm if y is not None]))
    hostsnamesmstring = map(lambda x: x.encode('ascii'), hostsnamesmshort)

    hostnames = [x for x in allkeys('ip', servicenamefound['instances'])]
    hostsunicode = list(set([x for x in hostnames if x is not None])) #elimina repetidos y quita el formato unicode
    hosts = map(lambda x: x.encode('ascii'), hostsunicode)

    hostauxmasters =  [x for x in allkeys('ip', servicenamefound['auxmasters'])]
    hostsauxmastershort= list(set([y for y in hostauxmasters if y is not None]))
    hostsauxmasterstring = map(lambda x: x.encode('ascii'), hostsauxmastershort)

    hostauxslaves =  [x for x in allkeys('ip', servicenamefound['auxslaves'])]
    hostsnameauxslavesshort = list(set([y for y in hostauxslaves if y is not None]))
    hostsauxslavestring = map(lambda x: x.encode('ascii'), hostsnameauxslavesshort)

    total = hosts + hostsnamesmstring + hostsauxmasterstring + hostsauxslavestring
    totalhosts = list(set([a for a in total if a is not None]))   
#    print(totalhosts)
#    print"The hosts used in ",servicename, "are: "
       
    for k in totalhosts:
        if IPAddress(k).is_private():
           hostsipv4.append(((socket.inet_ntoa(struct.pack("!I", int(k))))))
#    fileout=open('temp.txt','w')
    for x in hostsipv4:
#	print x
       hostdomains.append(socket.getfqdn((x)))
#	fileout.write("%s\n" % socket.getfqdn((x)))
    #client = ParallelSSHClient(hostdomains)
    #output = client.run_command('uptime; free -g')
    bcommand = "uname -a"
    bashcommand(hostdomains, command)
#    for hos in output:
#	for line in output[hos].stdout:
#	    pprint ("Host %s - output: %s'" % (hos,line))



if __name__ == "__main__":
    """
    Main function of the script.
    """
    decip = 0
    searchpart = "/redirector/getServerList?name="
    parser = OptionParser()
    parser.add_option('-c', '--command', dest='command',
                      help='load, ram, space')
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')

    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment) or None
    servicename = options.servicename or None
    command = options.command or None
    os.system('clear')
    print('Processing....................................')

    if not all([envhost, servicename, command]):
        parser.print_help()
        plugin_exit(STATUS_CRIT,\
                   'Some parameter is missing, servers.py -c load -e prd -s fifa-2016-ps4', "")

#    decimalip = struct.unpack("!L", socket.inet_aton(ipi))[0]
    searchurl = envhost+searchpart+servicename
#    print("Redirector URL", searchurl)
    searchinchredirector(searchurl+"$", servicename, command)

