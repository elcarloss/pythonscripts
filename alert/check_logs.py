import json
import urllib3
import xmltodict
import io
import os
import smtplib
import socket
import struct
import sys
import requests
import xmltodict
from optparse import OptionParser
from yaml import load, dump
from deepdiff import DeepDiff
from time import gmtime, strftime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)


ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='


BADWORDS = ["iterable_item_added"] 

def purge_dublicates(X):
    unique_X = []
    for i, row in enumerate(X):
        if row not in X[i + 1:]:
            unique_X.append(row)
    return unique_X


def gethostfromcoreslaves(titledict, url):
    global logdir
    lstinstances = []
    s = []
    print("TITLE: ",url)
#    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance']:
#        k = ['']
#        k = y.items()[1]
#        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1])])
#        w = k[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']
#        h = socket.getfqdn(str(int2ip(int(w))))
#        print(str(y.items()[4][1]),h)
    for b in titledict['serverlist']['servers']['serverinfodata']['instances']['serverinstance']:
        o = ['']
        o = b.items()[1]
        p = b.items()[0][1]     
        s.append(p)
        t = ((o)[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['ip'])
        j = str(int2ip(int(t)))
        g = socket.getfqdn(j)
#        print(str(b.items()[4][1]),g)
#        lstinstances.append([str(b.items()[4][1]),g])
        logdir = list(set(s))
        lstinstances.append(g)
    return(list(set(lstinstances)))
#        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1])])

#     instancesdct.update({TITLESALERTS.keys()[con]:lstinstances2})



def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))



def main(argv):
    """
    Main function of the script.
    """
    parser = OptionParser()
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-b', '--begin', dest='begin',
                             help='Begin Matching Time i.e: 2012/03/25-14:56')
    parser.add_option('-f', '--finish', dest='finish',
                      help='End Matching Time i.e: 2012/03/25-14:56')
    parser.add_option('-o', '--total', dest='total',
                      help='Environment prod, cert, dev, test')

    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment, None)
    servicename = options.servicename or None
    begin = options.begin or None
    finish = options.finish or None
    total = options.total or None
    if not all([envhost, servicename, begin, finish, total]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, chkblz.py -H <hostname> -e <environment> \
                   -s <servicename> -i <instancename> -p <port>', "")
    print("Data to search")
    print("Servicename: ", servicename)
    print("Environment: ", envhost)
    print("Begin time: ", begin)
    print("Finish time: ", finish)
    print("Total search: ", total)

#    try:
#        ipurl = socket.gethostbyname(hostname)
#        ipi = ipurl
#    except socket.gaierror:
#        plugin_exit(STATUS_UNK, 'Dns Error', "")

#    decimalip = from_string(ipi)
    searchurl = envhost+SEARCH+servicename+"$"
    print("Redirector URL", searchurl)

    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str


    print "Processing ....."
    lstinstances2 = []
    http2v2 = urllib3.PoolManager(retries=False)
    titlexmlv2 = http2v2.request('GET', searchurl, timeout=8)
    titledictv2 = xmltodict.parse(titlexmlv2.data)
    instancs = gethostfromcoreslaves(titledictv2, searchurl)
    print("Instances and hostnames: ", instancs)
    print("Logdir: ", logdir)

if __name__ == "__main__":
    main(sys.argv[1:])

