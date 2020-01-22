import sys
from optparse import OptionParser
import json
import urllib3
import urllib2
import json
import sys
import csv
import xmltodict
import os
import socket
import struct
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)
import pprint
import xml.etree.ElementTree as etree
import time
import requests
PATH = os.environ['HOME']+'/p4/gosops/tools/gos24x7/toolbox/Classes/Redirector'
#PATH = os.environ['HOME']+'/pyvirtual/scripts/Classes/Redirector'
sys.path.insert(0, PATH)
from redirclass import redir, RedirectorError
sys.path.insert(0, PATH)
from redirclass import redir, RedirectorError

ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='
GETSTATUS = '/blazecontroller/getStatus'


def searchlogdir(url):
    req = requests.get(url, timeout=5)
    data = etree.fromstring(req.content)
    for father in data.findall('.//commandlineargs'):
        for child in father:
            if child.attrib == {'key': '--logdir'}:
                logdir = child.text
        return(logdir)

def searchredirector2(schurl, sername, env):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

    TITLESALERTS = {sername:schurl}
    con = 0
    nodata = 0
    instancesdct = {}
    instotal = []
    print "Processing ....."
    redirector = redir(env, sername)
    if not redirector.get_servicenames():
        print("Servicename Not exists")
        sys.exit()

    cwd = redirector.get_cwd()
    statuslst = []
    cl = "0"
    allinstances = redirector.get_instanceslistwithports()

    if allinstances == None:
        print("Servicename Not exists")
        sys.exit()
    insta = []
    for x in allinstances:
        if "coreSlave" in x[0]:
            insta.append(x[0])
            insta.append(socket.getfqdn(x[2]))
            insta.append(x[3])
    print("Instancias Coreslave",insta)
    searchurldata = 'http://'+ insta[1]+':'+insta[2]+GETSTATUS
    logdirv = searchlogdir(searchurldata)				
    print("LOGDIR =", logdirv)


    buildlocation = redirector.get_buildlocation()
    depot = redirector.get_depotlocation()
    cl = redirector.get_blazeversion()
    print("\n---------- DETAILED DATA ---------\n\n")
    print("Servicename: ", sername)
    print("CL: ", cl)
    print("Depot Location: ", depot)
    print("Build Location: ", buildlocation)
    print("Running in the path: ", cwd)
    			
#    print("Instancias: ", insta)

def main(argv):
    """
    Main function of the script.
    """
    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')


    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment, None)
    servicename = options.servicename or None
    if not all([envhost, servicename]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, instancesredir.py -e <environment> -s <servicename>', "")

    searchurl = envhost+SEARCH+servicename+"$"
#    x = getInfo(servicename,options.environment)
    enviro = options.environment

    searchredirector2(searchurl, servicename, enviro)
	

if __name__ == "__main__":
    main(sys.argv[1:])
