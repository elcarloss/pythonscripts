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
from optparse import OptionParser
import requests
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)
import xmltodict


ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='
GETSTATUS = '/blazecontroller/getStatus'
KEYINSTANCENAMEAUXLSTB15 = (['search', 'gr', 'cmrAux', 'search', 'mm', 'osdkAux', 'maut', 'mutAux',
                             'custom', 'onlinecareer', 'nhlAux', 'odtAux', 'nba', 'anarchists',
                             'realtime', 'spl', 'chl', 'item', 'autolog', 'kickback', 'competitive',
                             'nonZdt', 'rsp', 'madAux', 'cmwAux', 'da3Aux'])
KEYINSTANCENAMEMASTERLSTB15 = (['config', 'core', 'coreNS', 'rsp', 'custom', 'osdkAux', 'nba',
                                'cmrAux', 'aux', 'chl', 'spi', 'item', 'kick', 'spl', 'competitive',
                                'nonZdt', 'onlinecareer', 'odtAux', 'madAux', 'cmwAux', 'da3Aux'])
BLAZEVERSIONS = ["13", "14", "15"]

def existkeywordininstanceinservice(xmlredir, instanceargument, auxinstancetype):
    """
    verify if the instance inservice tag is "0" (bad state)  or "1" (good state)
    """
    leninstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']
                                 [auxinstancetype]['serverinstance'])
    for x in range(leninstancesredirector):
        if instanceargument == (xmlredir['serverlist']['servers']['serverinfodata'][auxinstancetype]
                                ['serverinstance'][x]['instancename']):
            if (xmlredir['serverlist']['servers']['serverinfodata'][auxinstancetype]
                    ['serverinstance'][x]['inservice']) == "0":
                return 0
            else:
                return 1
    return 0
         

def validatelenxml(reqcontent):
    """
    Check the lenght of the xml if is < than 154 then the xml is not
    correct and shows an error
    """
    if len(reqcontent) < 154:
        plugin_exit(STATUS_UNK, "The xml does not appear to have any style information " +
                    "associated with it / error at url - Validate Lenght Funciont", "")
        return 0
    else:
        return 1

def cutstring(insargument, instanceargumentmaster):
    """
    cut the instanceargument to return keywords to validate function
    and helping it to know if the instance is auxslave, auxmaster
    or core
    """
    indexkeywords = insargument.rfind("Slave")
    indexkeywordm = insargument.rfind("Master")
    return(insargument[0:indexkeywords], insargument[0:indexkeywordm])


def validateinserviceinstances(xmlredir, instanceargument):
    """
    Validates if the instance is inservice 1 (ok) or
    inservice 0 (Stuck)
    """
    instanceargumentmaster = "temp"
    instancekeywords, instancekeywordm = cutstring(instanceargument, instanceargumentmaster)
    if instancekeywords in KEYINSTANCENAMEAUXLSTB15:
        auxinstancetype = 'auxslaves'
        if existkeywordininstanceinservice(xmlredir, instanceargument, auxinstancetype):
            return 1
        return 0
    elif instancekeywordm in KEYINSTANCENAMEMASTERLSTB15:
        auxinstancetype = 'auxmasters'
        if existkeywordininstanceinservice(xmlredir, instanceargument, auxinstancetype):
            return 1
        return 0
    elif instancekeywords == "core":
        auxinstancetype = 'instances'
        if existkeywordininstanceinservice(xmlredir, instanceargument, auxinstancetype):
            return 1
        return 0


def searchinchredirector(schurl, sername, insargument, decip):
    """
    Searching and getting the xml of redirector, analysing the xml file converting
    to a dictionary.
    This function checks if the service name, ip and instance exists in redirector 
    xml file. If the instance exist it validates if is working fine or if is stuck
    (inservice 0 or 1)
    """

    try:
        reqredirectorurl = requests.get(schurl, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_UNK, 'Failed to get the redirector xml', "")
    xmlredirector = xmltodict.parse(reqredirectorurl.text)
    reqcontentredir = reqredirectorurl.content
    validatelenxml(reqcontentredir)
    if all([insargument in reqredirectorurl.content, sername in reqredirectorurl.content,
            str(decip) in reqredirectorurl.content, "configMaster" in insargument]):
        plugin_exit(STATUS_OK, "The process is registered in Redirector configMASTER ", "")
    elif all([insargument in reqredirectorurl.content, sername in reqredirectorurl.content,
              str(decip) in reqredirectorurl.content]) and validateinserviceinstances(xmlredirector, insargument):
        plugin_exit(STATUS_OK, "The process is registered in Redirector V15 ", "")
    else:
        plugin_exit(STATUS_CRIT, "Servicename or Instance not registered on Redirector" +
                    " / Stuck Blaze Instance", "")

def searchingetstatusxml(urldata, iargument, sname):
    """
    This function allows to know if the instance and servicename processes exists in
    the hostname given as a parameter.
    """

    try:
        req = requests.get(urldata, timeout=2)
    except Exception as e:
        plugin_exit(STATUS_CRIT, "Servicename or instance not registered on Redirector -" +
                    "Failed to get the getstatus xml", "")
    reqcontent = req.content
    validatelenxml(reqcontent)
    xmlblaze = xmltodict.parse(req.text)
    blazever = xmlblaze['serverstatus']['version']['version']
    blazeversion = blazever.split()[1]
    bversion = blazeversion[0:2]
    if bversion in BLAZEVERSIONS:
        if not all([iargument in req.content, sname in req.content]):
            plugin_exit(STATUS_CRIT, "Servicename or instance not registered on Redirector - Stop in Geststatus", "")
    else:
        plugin_exit(STATUS_UNK, "This version check only suport blaze 13,14 and 15", "")




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
    searchurl = envhost+SEARCH+servicename+"$"
    searchurldata = 'http://'+ hostname+':'+portarg+GETSTATUS
    searchingetstatusxml(searchurldata, instanceargument, servicename)
    searchinchredirector(searchurl, servicename, instanceargument, decimalip)

if __name__ == "__main__":
    main(sys.argv[1:])
