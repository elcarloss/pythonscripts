#!/usr/bin/python27
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Date: March, 2017

"""
Monitoring alert to verify if a Blaze process is running and properly registered on gosredirector.
"""

import sys
import socket
import struct
import urllib3
import xmltodict
from lxml import etree
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
from optparse import OptionParser


environments = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
searchpart = '/redirector/getServerList?name='
searchpartgetstatus = '/blazecontroller/getStatus'


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

def searchinchredirector(searchurl, servicename, instanceargument, decimalip):
    """
    Searching and getting the xml of redirector.
    """
    servicenamefound = {}
    allservicenamesfound = []
    http2 = urllib3.PoolManager(retries=False)

    try:
        reqredirectorurl = http2.request('GET', searchurl, timeout=2)
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

    validate = lambda value: value in get_all_leaf_nodes(servicenamefound)
    values = [instanceargument, servicename, str(decimalip)]
    if not all([validate(v) for v in values]):
        plugin_exit(STATUS_CRIT, "Servicename or instance not found", "")
    else:
        plugin_exit(STATUS_OK, "The process is registered in Redirector", "" )
    #if not (instanceargument in get_all_leaf_nodes(servicenamefound) and
    #        servicename in get_all_leaf_nodes(servicenamefound) and
    #        str(decimalip) in  get_all_leaf_nodes(servicenamefound)):
    #    plugin_exit(STATUS_CRIT, "Servicename or instance not registered on Redirector", "")
    #else:
    #    plugin_exit(STATUS_OK, "The process is correctly registered in Redirector", "")

def searchingetstatusxml(searchurldata, instanceargument, servicename):
    """
    Searching and getting the xml of gestatus link.
    """
    http = urllib3.PoolManager(retries=False)

    try:
        req = http.request('GET', searchurldata, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_UNK, 'Failed to get the getstatus xml', "")

    dicxmlgetstatus = xmltodict.parse(req.data)
    if not (instanceargument in get_all_leaf_nodes(dicxmlgetstatus) and
            servicename in get_all_leaf_nodes(dicxmlgetstatus)):
        plugin_exit(STATUS_CRIT, "Servicename or instance not registered on Redirector", "")


def main(argv):
    """
    Main function of the script.
    """
    servicename = ''
    instanceargument = ''
    hostname = ''
#    environments = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
#                    'cert': 'http://internal.gosredirector.scert.ea.com:42125',
#                    'dev': 'http://internal.gosredirector.online.ea.com:42125',
#                    'test': 'http://internal.gosredirector.stest.ea.com:42125'}
#    searchpart = '/redirector/getServerList?name='
#    searchpartgetstatus = '/blazecontroller/getStatus'
    portarg = ''
    parser = OptionParser()
    parser.add_option('-H', '--hostname', dest='hostname',
	                     help='Hostname to check in redirector')
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')
    parser.add_option('-i', '--instancename', dest='instancename',
                      help='name of the instance to check, for example coreSlave351')
    parser.add_option('-p', '--port', dest='port',
                      help='port to obtain the goscc getstatus xml file, for example 10')

    (options, args) = parser.parse_args()

    if not options.hostname and not options.environment and not options.servicename and \
       not options.instancename and not options.port:
        parser.print_help()
        plugin_exit(STATUS_WARN, "The correct sintaxis is: chkblz.py -H <hostname> \
                    -e <environment> -s <servicename> -i <instancename> -p <port>", "")

    if options.environment in environments.keys():
        envhost = environments.get(options.environment)

    hostname = options.hostname
    servicename = options.servicename
    instanceargument = options.instancename
    portarg = options.port

    if not all([hostname, envhost, servicename, instanceargument, portarg]):
        plugin_exit(STATUS_CRIT,\
                   'Some parameter is missing, chkblz.py -H <hostname> -e <environment> \
                   -s <servicename> -i <instancename> -p <port>', "")

    try:
        ipurl = socket.gethostbyname(hostname)
        ipi = ipurl
    except socket.gaierror:
        plugin_exit(STATUS_CRIT, 'Dns Error', "")

    decimalip = struct.unpack("!L", socket.inet_aton(ipi))[0]
    searchurl = envhost+searchpart+servicename
    searchurldata = 'http://'+ hostname+':'+portarg+searchpartgetstatus
    print("Redirector", searchurl)
    print(searchurldata)
    searchingetstatusxml(searchurldata, instanceargument, servicename)
    searchinchredirector(searchurl, servicename, instanceargument, decimalip)


if __name__ == "__main__":
    main(sys.argv[1:])
