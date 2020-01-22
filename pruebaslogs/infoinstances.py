#!/usr/bin/python2.7
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# February, 2018

# <22-Feb-2018> <Carlos Alarcon>
# <Check Instances, hostnames, ip and Inservice or Not> 


"""
Tool to obtain servicename data like, instancenames, host, ip and Inservice or Not
Valid only for Blaze versions 3, 13, 14 & 15 titles
"""
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


HTTP = "http://"
GETSTATUS = "/blazecontroller/getStatus"

def checkerrors(url):
    req = requests.get(url, timeout=5)
    data = etree.fromstring(req.content)
#    for logger in data.findall('.//loggermetrics'):
#        x = logger.find('categories')
#        for h in x:
            #print(h.attrib)
#            pos = h.attrib
#            if pos['key'] == "connection":
#                for w in h.findall('.//entry'):
#                    err = w.attrib
#                    errvalue = w.text
#                    url = w.text
#                    if err['key'] == "ERR":
#                        return(url)
#                    else:
#                        url = 0
#                        return(url)
##    for i in data.findall('.//version/version'):
##        cl = i.text
#        print("CL: ",cl)
##        return(cl)

    for i in data.findall('.//fibermanagerstatus/cpuusageforprocesspercent'):
        cl = i.text
#        print("CL: ",cl)
        return(cl)


def getcl(url):
    reqcl = requests.get(url, timeout=5)
    datacl = etree.fromstring(reqcl.content)
#    for i in datacl.findall('.//version/version'):   
#        return(i.text)
    for i in datacl.findall('.//fibermanagerstatus/cpuusageforprocesspercent'):
        return(i.text)

        


def getInfo(service,env):
    try:
        data = urllib2.urlopen('http://torch.gameservices.ea.com/metadata/titleData.json')
    except:
        data = urllib2.urlopen('http://gosprodbeapp0008.abn-sjc.ea.com/portal/titleData.json')

    salida = json.load(data)
    servicess = []
    listbz = []
    listdb = []
    listds = []
    listrd = []
    listpt = []
    listjn = []
    listdc = []
    for product in salida:
        for blaze in product['serviceDescriptions']:
            if service == blaze['serviceName'] and env == blaze['environment']:
                try:
                    listbz = [x for x in blaze['appHosts']]
                except:
                    pass

                try:
                    listdb = [x[:-5] for x in blaze['databaseInstances']]
                except:
                    pass

                try:
                    listds = [x[:-6] for x in blaze['servulatorInstances']]
                except:
                    pass

                try:
                    listrd = [x for x in blaze['redisClusters']['main']]
                except:
                    pass

                try:
                    listpt.append(blaze['mdmProjectTitle'])
                except:
                    pass


                try:
                    listjn.append(blaze['jiraOTName'])
                except:
                    pass

                try:
                    listdc.append(blaze['dataCenter'])
                except:
                    pass



    return sorted(listbz), sorted(listdb), sorted(listds), sorted(listrd), sorted(servicess), sorted(listpt), sorted(listjn), sorted(listdc)

ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='



def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def searchredirector2(schurl, sername, env, titledata):
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
#    print(allinstances)
    if allinstances == None:
        print("Servicename Not exists")
        sys.exit()
    for x in range(len(allinstances)):
        allinstances[x].insert(len(allinstances[x]), socket.getfqdn(allinstances[x][2]))
##        allinstances[x].insert(len(allinstances[x]), HTTP + allinstances[x][4] + ":" + allinstances[x][3] + GETSTATUS)
        status = HTTP + allinstances[x][4] + ":" + allinstances[x][3] + GETSTATUS
        allinstances[x].insert(len(allinstances[x]), checkerrors(status))
#        allinstances[x].insert(len(allinstances[x]), getcl(status))        
    masterl = list(redirector.get_masterinfo())
    masterl.insert(len(masterl), socket.getfqdn(masterl[2]))
    allinstances.insert(0, masterl)
#    print(statuslst)    
    set_hosts = []
    for instance in allinstances:
         set_hosts.append(socket.gethostbyaddr(instance[2])[0])
    allhosts = list(set(set_hosts))
#    status = HTTP + allinstances[0][3] + ":" + allinstances[1][3] + GETSTATUS
#    print("Status 1: ", status)
#    print("Errorrsssssssssssssssssssssss in instances___________________________________________________________________________________: ",checkerrors(status))
    buildlocation = redirector.get_buildlocation()   
    depot = redirector.get_depotlocation()
    cl = redirector.get_blazeversion()
# socket.getfqdn(str(int2ip(int(y.items()[1][1]
    print("\n---------- DETAILED DATA ---------\n\n")
    print("Servicename: ", sername)
    print("Project Title: ", titledata[5])
    print("JiraOTName: ", titledata[6])
    print("Datacenter: ", titledata[7])
    print("CL: ", cl)
    print("Depot Location: ", depot)
    print("Build Location: ", buildlocation)
    print("Running in the path: ", cwd)
    print("\n---------- INSTANCES ---------\n ")
    if allinstances:
        for x in allinstances:
            if x[1] == '0':
                print("---------------------------------------------------------------------------")
                pprint.pprint(x)
                print("---------------------------------------------------------------------------")
            else:
                print(' '.join(x))
    else:
        print("There's not instances available") 
    print("Number of instances used in this title: ",len(allinstances))
    print("Hosts used in this title: ",allhosts,len(allhosts))
    print ("---------------------------------------------------------------------------------------")




def from_string(ipv):
    "Convert dotted IPv4 address to integer."
    return reduce(lambda a, b: a<<8 | b, map(int, ipv.split(".")))


def main(argv):
    """
    Main function of the script.
    """
    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')
    parser.add_option('-a', '--al', dest='al',
                      help='Show instances information, type 1 to activate', default=0)
    parser.add_option('-u', '--cpu', dest='cpu',
                      help='Show instances cpu percent usage, type 1 to activate', default=0)
    parser.add_option('-c', '--cl', dest='cl',
                      help='Show instances CL information, type 1 to activate', default=0)

    parser.add_option('-d', '--dirtycast', dest='dirtycast', 
                      help='Dirtycasts boxes, type 1 to show dirtycasts', default=0)
    parser.add_option('-r', '--redis', dest='redis',
                      help='Redis Instances', default=0)
    parser.add_option('-p', '--apphosts', dest='apphost', 
                      help='App Hosts', default=0)
    parser.add_option('-b', '--database', dest='database', 
                      help='Database boxes', default=0)
   

    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment, None)
    servicename = options.servicename or None
    if not all([envhost, servicename]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, instancesredir.py -e <environment> -s <servicename>', "")
    al = options.al or None
    dirtycast = options.dirtycast or None
    redis = options.redis or None
    apphost = options.apphost or None
    database = options.database or None
    cl = options.cl or None
    cpu = options.cl or None

#    print(servicename)
#    print(envhost) 
    searchurl = envhost+SEARCH+servicename+"$"
    x = getInfo(servicename,options.environment)
    enviro = options.environment

    if al:
        print(searchurl)
        #searchinchredirector(searchurl, servicename, x)
        searchredirector2(searchurl, servicename, enviro, x)

#    print("Valor de la lista X")
#    pprint.pprint (x)
    if apphost:
        if x[0]:
           print("\n--------- APP HOSTS ---------\n")
           pprint.pprint(x[0])
        else:
            print("--------- THERE'S NOT EXIST APP HOSTS FOR THIS TITLE ---------\n")

    if dirtycast:
        if x[2]:
            print("\n--------- DEDICATED SERVERS ---------\n")
            pprint.pprint(x[2])
        else:
            print("--------- THERE'S NOT EXIST DEDICATED SERVERS FOR THIS TITLE OWNED BY EA ---------\n")

    if redis:
        if x[3]:
            print("\n--------- REDIS INSTANCESS ---------\n")
            pprint.pprint(x[3])
        else:
            print("--------- THERE'S NOT EXIST REDIS INSTANCES FOR THIS TITLE  ---------\n")

    if database:
        if x[1]:
            print("\n--------- DATABASE BOXES ---------\n")
            pprint.pprint(x[1])
        else:
            print("--------- THERE'S NOT EXIST DATABASE BOXES FOR THIS TITLE  ---------\n")



#If not options has been choosen 
    if (al == None and apphost == None and dirtycast == None and redis == None and apphost == None and database == None):
        os.system("clear")
        print("(----------- NOT VALID OPTIONS HAS BEEN CHOOSEN ----------)")
        print("The sintaxis for this script is:")    
        print("instancesredir.py -e <environment> -s <servicename> -a 1 -d 1 -r 1 -p 1 -b 1")
        print("Where -a 1 -d 1 -r 1 -p 1 and -b 1 are optional parameters")
        print("-a 1 shows a detailed info for the service, instancenames, hosts, ips and inservice status for the instances")
        print("-d 1 shows the dirtycasts boxes for the title")
        print("-r 1 shows the redis instances for this title")
        print("-b 1 shows the databases boxes for this title")



if __name__ == "__main__":
    main(sys.argv[1:])
