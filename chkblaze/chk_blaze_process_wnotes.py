#!/usr/bin/python2.7
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Date: March, 2017

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


def existkeywordininstanceinservice(leninstancesinredirector, xmlredir, instanceargument, auxinstancetype):
    for x in range(leninstancesinredirector):
        if instanceargument in (xmlredir['serverlist']['servers']['serverinfodata'][auxinstancetype]['serverinstance'][x]['instancename']):
            if (xmlredir['serverlist']['servers']['serverinfodata'][auxinstancetype]['serverinstance'][x]['inservice']) == "0":
                print("Instancia Encontrada con 0 en servicio")
                return(0)
    return(1)


def cutstring(insargument, instanceargumentmaster):
    leninstance = len(insargument)
    indexkeywords = insargument.rfind("Slave")
    indexkeywordm = insargument.rfind("Master")
    return(insargument[0:indexkeywords], insargument[0:indexkeywordm])

def validateinservicecoreslaves(xmlredir, instanceargument, blazeversion):
    print("Entro a validateservice ", blazeversion[0:2])
    if "15" in  blazeversion[0:2]:
        print("Entro a validateservicecore en 15 blaze")
        instanceargumentmaster = "temp"
        instancekeywords, instancekeywordm = cutstring(instanceargument, instanceargumentmaster)
        print("Instancia parte clave de auxslave: ", instancekeywords)
        print("Instancia parte clave de master: ", instancekeywordm)

        if instancekeywords in KEYINSTANCENAMEAUXLSTB15:
            auxinstancetype = 'auxslaves'            
            lenauxslaveinstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']['auxslaves']['serverinstance'])
            print("AuxSlavesInstances Section", lenauxslaveinstancesredirector)
            if existkeywordininstanceinservice(lenauxslaveinstancesredirector, xmlredir, instanceargument, auxinstancetype):
                return(1)
            return(0)
        elif instancekeywordm in KEYINSTANCENAMEMASTERLSTB15:
            auxinstancetype = 'auxmasters'
            lenmasterinstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance'])
            print("MasterInstances Section", lenmasterinstancesredirector)
            if existkeywordininstanceinservice(lenmasterinstancesredirector, xmlredir, instanceargument, auxinstancetype):
                return(1)
            return(0)
        elif instancekeywordm == "core":
            auxinstancetype = 'instances'
            lenslaveinstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']['instances']['serverinstance'])
            print("SlavesInstances Section", lenslaveinstancesredirector)
            if existkeywordininstanceinservice(lenslaveinstancesredirector, xmlredir, instanceargument, auxinstancetype):
                return(1)
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

    if len(reqredirectorurl.content) < 100:
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information \
                                 associated with it", "")
    xmlredirector = xmltodict.parse(reqredirectorurl.text)

    if "15" ==  blazeversion[0:2]:
        lenxmlinstancesredirector = len(xmlredirector['serverlist']['servers']['serverinfodata']['instances']['serverinstance'])
        print("La instancia esta en reqredirector 15???", insargument in reqredirectorurl.content)
        print("El servicename esta en reqredirector 15???", sername in reqredirectorurl.content)
        print("La ip decimal esta en reqredirector 15???", str(decip) in reqredirectorurl.content)
        print("La instancia esta activa (1) en reqredirector???", validateinservicecoreslaves(xmlredirector, insargument, blazeversion))


        if ((insargument in reqredirectorurl.content) and
                (sername in reqredirectorurl.content) and
                (str(decip) in reqredirectorurl.content) and
                (validateinservicecoreslaves(xmlredirector, insargument, blazeversion))):
            plugin_exit(STATUS_OK, "The process is registered in Redirector", "")
        else:
            plugin_exit(STATUS_CRIT, "Servicename or Instance not registered on Redirector / Stuck Instance blaze otros aparte de 3", "")
    else:
        lenxmlinstancesredirector = len(xmlredirector['serverlist']['servers']['serverinfodata']['instances']['serverinstance'])
        print("Version 3 de blaze")
    
        if ((insargument in reqredirectorurl.content) and (sername in reqredirectorurl.content) and (str(decip) in reqredirectorurl.content)):
            plugin_exit(STATUS_OK, "The process is registered in Redirector V3", "")
        else:
            plugin_exit(STATUS_CRIT, "Servicename or Instance not registered on Redirector / Stuck Instance blaze V3", "")



def searchingetstatusxml(urldata, iargument, sname, instanceargoldblaze):
    """
    Searching instancename and servicename in getstatus xml
    """
    global blazeversion
    try:
        req = requests.get(urldata, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_CRIT, 'Servicename or instance not registered on Redirector - Failed to get the getstatus xml', "")
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
    print("La ip decimal es: ",decimalip)
    instanceargumentoldblaze = instanceargument.replace('-', '_')
    searchurl = envhost+SEARCH+servicename+"$"
    searchurldata = 'http://'+ hostname+':'+portarg+GETSTATUS
    print("Redirector URL",searchurl)
    print("GetStatus URL",searchurldata)
    searchingetstatusxml(searchurldata, instanceargument, servicename, instanceargumentoldblaze)
    print("Blaze Version: ", blazeversion)
    searchinchredirector(searchurl, servicename, instanceargument, decimalip, blazeversion)

if __name__ == "__main__":
    main(sys.argv[1:])
