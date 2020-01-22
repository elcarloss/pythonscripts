#!/usr/bin/python2.7
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Update: September, 2017

"""
Monitoring alert to verify if a Blaze process is running and properly registered on gosredirector.
"""
import sys
import socket
import requests
import xmltodict
from optparse import OptionParser
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)
import validate


ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='
GETSTATUS = '/blazecontroller/getStatus'
KEYINSTANCENAMEAUXLSTB15 = (['search','gr','cmr','search','mm','osdkAux','maut','mut','custom',
                            'onlinecareer','nhlAux','odtAux','nba','anarchists','realtime','spl',
                            'chl','item','autolog','kickback''competitive'])
KEYINSTANCENAMEMASTERLSTB15 = (['config','core','coreNS','rsp','custom','osdkAux','nba','cmrAux',
                              'aux','chl','spi','item','kick','spl','competitive'])



def validatelenxml(reqcontent):
    if len(reqcontent) < 154:
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information" +
                                 "associated with it / error at url", "")
        return(0)
    else:
        return(1)


def searchinchredirector(schurl, sername, insargument, decip, blazeversion):
    """
    Searching and getting the xml of redirector.
    """

    try:
        reqredirectorurl = requests.get(schurl, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_UNK, 'Failed to get the redirector xml', "")

    xmlredirector = xmltodict.parse(reqredirectorurl.text)
    reqcontentredir=reqredirectorurl.content
    if not validatelenxml(reqcontentredir):
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information associated " + 
                    "with it / error at url", "")
    instanceinservice = validate.Validateinservice(xmlredirector, insargument)
    print("auxmasters", instanceinservice.auxmasters())
#    print(instanceinservice.auxslaves())
#    print(instanceinservice.coreslaves())
    print("Valor de Instancia para validar servicio",instanceinservice)
#    if "15" ==  blazeversion[0:2]:
#        auxslaves = Validateinservice(xmlredirector, insargument)
#        if all ([insargument in reqredirectorurl.content, sername in reqredirectorurl.content, 
#                str(decip) in reqredirectorurl.content]) and validateinservice.auxslaves(xmlredirector, insargument):
#            plugin_exit(STATUS_OK, "The process is registered in Redirector" , "")
#        else:
#            plugin_exit(STATUS_CRIT, "Servicename or Instance not registered on Redirector" + 
#                        " / Stuck Instance blaze ", "")
#    else:
#        print("Version 3 de blaze")
#        if all ([insargument in reqredirectorurl.content, sername in reqredirectorurl.content, 
#                (str(decip) in reqredirectorurl.content)]):
#            plugin_exit(STATUS_OK, "The process is registered in Redirector B3", "")
#        else:
#            plugin_exit(STATUS_CRIT, "Servicename or Instance not registered on Redirector " + 
#                        "/ Stuck Instance blaze V3", "")


def searchingetstatusxml(urldata, iargument, sname, instanceargoldblaze):
    """
    Searching instancename and servicename in getstatus xml
    """
    global blazeversion

    try:
        req = requests.get(urldata, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_CRIT, 'Servicename or instance not registered on Redirector - \
                    Failed to get the getstatus xml', "")
    reqcontent = req.content
    if not validatelenxml(reqcontent):
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information \
                                 associated with it / error at url", "")

    dicxmlgetstatus = xmltodict.parse(req.content)
    xmlblaze = xmltodict.parse(req.text)
    blazever = xmlblaze['serverstatus']['version']['version']
    blazeversion = blazever.split()[1]
    
    if not ((iargument in req.content) and (sname in req.content)
            or instanceargoldblaze in req.content):
        plugin_exit(STATUS_CRIT, "Servicename or instance not registered on Redirector", "")


def from_string(ipv):
    "Convert dotted IPv4 address to integer."
    return reduce(lambda a, b: a<<8 | b, map(int, ipv.split(".")))


def main(argv):
    """
    Main function of the script.
    """
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

    envhost = ENVIRONMENTS.get(options.environment, None)
    hostname = options.hostname or None
    servicename = options.servicename or None
    instanceargument = options.instancename or None
    portarg = options.port or None
    if not all([hostname, envhost, servicename, instanceargument, portarg]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, chkblz.py -H <hostname> -e <environment> \
                   -s <servicename> -i <instancename> -p <port>', "")

    try:
        ipurl = socket.gethostbyname(hostname)
        ipi = ipurl
    except socket.gaierror:
        plugin_exit(STATUS_UNK, 'Dns Error', "")

    decimalip = from_string(ipi)
    instanceargumentoldblaze = instanceargument.replace('-', '_')
    searchurl = envhost+SEARCH+servicename+"$"
    searchurldata = 'http://'+ hostname+':'+portarg+GETSTATUS
    print("Redirector URL",searchurl)
    print("GetStatus URL",searchurldata)
    searchingetstatusxml(searchurldata, instanceargument, servicename, instanceargumentoldblaze)
    searchinchredirector(searchurl, servicename, instanceargument, decimalip, blazeversion)

if __name__ == "__main__":
    main(sys.argv[1:])
