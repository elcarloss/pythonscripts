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


def searchinchredirector(schurl, sername, titledata):
    """
    Searching and getting the xml of redirector, analysing the xml file converting
    to a dictionary.
    This function checks if the service name, ip and instance exists in redirector
    xml file. If the instance exist it validates if is working fine or if is stuck
    (inservice 0 or 1)
    """
					
					
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str

#    with open('instances2.json') as data_file:
#        data_loaded = load(data_file)
    TITLESALERTS = {sername:schurl}
    con = 0
    nodata = 0
    instancesdct = {}
    instotal = []
    print "Processing ....."
    for x in TITLESALERTS.values():
        lstinstances2 = []
        cl = []
        depot = []
        buildlocation = []
        newList = []
        lstinstancesauxmasters = []
        lstinstancescoreslaves = []
        lstinstancesauxslaves = []
        titledictv2 = {}
        http2v2 = urllib3.PoolManager(retries=False)
        titlexmlv2 = http2v2.request('GET', x, timeout=3)
        titledictv2 = xmltodict.parse(titlexmlv2.data)
#        titlejsonv2 = json.dumps(titledictv2)
        if titledictv2['serverlist'] == None:
            print("Blaze Version not supported / Servicename Not exists")
            sys.exit()   
        cl.append(str(titledictv2['serverlist']['servers']['serverinfodata']['version']))
        depot.append(str(titledictv2['serverlist']['servers']['serverinfodata']['depotlocation']))
        buildlocation.append(str(titledictv2['serverlist']['servers']['serverinfodata']['buildlocation']))

        lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['instancename']))
        lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['inservice']))
        lstinstances2.append(socket.getfqdn(str(int2ip(int(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip'])))))
        lstinstances2.append(str(int2ip(int(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))))

        for i in cl:
            newList.append(i.split(" ")[1])
        for h in newList:
            parts = h.split(".")[0]
#        print(parts)
        if parts in ["3"]:
            print("Blaze Version 3")
        try: 
            for y in titledictv2['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance']:
                lstinstancesauxmasters.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip'])))), int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))])

#CORESLAVES INSTANCES
            for y in titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']:
                s = []
                o = ['']
                o = y.items()[1]
                p = y.items()[0][1]
                s.append(p)
                t = ((o)[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['ip'])
                j = str(int2ip(int(t)))
                g = socket.getfqdn(j)
                lstinstancescoreslaves.append([str(y.items()[4][1]), str(y.items()[5][1]), str(g),j])
#AUXSLAVES INSTANCES

            for y in titledictv2['serverlist']['servers']['serverinfodata']['auxslaves']['serverinstance']:
                lstinstancesauxslaves.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip'])))), int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))])
        except:
            try:
#CORESLAVES INSTANCES
                for y in titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']:
                    s = []
                    o = ['']
                    o = y.items()[1]
                    p = y.items()[0][1]
                    s.append(p)
                    t = ((o)[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['ip'])
                    j = str(int2ip(int(t)))
                    g = socket.getfqdn(j)

                    lstinstancescoreslaves.append([str(y.items()[4][1]), str(y.items()[5][1]), str(g),j])
               

            except:               
                print"error en slaves"
                lstinstancescoreslaves.append([(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['instancename'])), str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['inservice']), str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['hostname']), int2ip(int(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['ip'])))])                

#                print(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['instancename']))
#                print(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['inservice']))
#                print(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['hostname']))
#                print(int2ip(int(str(titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo'][0]['address']['valu']['ip']))))


        print("\n---------- DETAILED DATA ---------\n\n")
        print("Servicename: ", sername)
        print("Project Title: ", titledata[5])
        print("JiraOTName: ", titledata[6])
        print("Datacenter: ", titledata[7])
        print("CL: ", cl)
        print("Depot Location: ", depot)
        print("Build Location: ", buildlocation)
        print("\n---------- INSTANCES ---------\n ")
        pprint.pprint(lstinstances2)
        if lstinstancesauxmasters:
            for x in lstinstancesauxmasters:
                if x[1] == '0':
                    print("---------------------------------------------------------------------------")
                    pprint.pprint(x)
                    print("---------------------------------------------------------------------------")
                else:
                    pprint.pprint(x)
        else:
            print("There's not exists auxmaster instances")
        if lstinstancesauxslaves:
            for x in lstinstancesauxslaves:
                if x[1] == '0':
                    pprint.pprint("---------------------------------------------------------------------------")
                    pprint.pprint(x)
                    print("---------------------------------------------------------------------------")
                else:
                    pprint.pprint(x)
        else:
            print("There's not exists auxSlave instances")
        if lstinstancescoreslaves:
            for x in lstinstancescoreslaves:    
                if x[1] == '0':
                    print("---------------------------------------------------------------------------")
                    print(x)
                    print("---------------------------------------------------------------------------")
                else:
                    pprint.pprint(x)
        else:
            print("There's not exists coreSlave instances")

        insnumber = 1+len(lstinstancesauxmasters)+len(lstinstancescoreslaves)+len(lstinstancesauxslaves)
        print("Running Instances: ",insnumber)
        print("\n")
        print("\n\n---------- RESUME DATA ----------\n\n")
        print("Hosts in: ", sername)
        hosts=[]
        hostssorted=[] 
        hosts.append(lstinstances2[2])
        for x in lstinstancesauxmasters:
            hosts.append(x[2])
        for w in lstinstancesauxslaves:
            hosts.append(w[2])
        for z in lstinstancescoreslaves:
            hosts.append(z[2])
        hostssorted=sorted(hosts)
        for x in set(list(hostssorted)):
            print x                             
        print("Number of hosts used in this title: ",len(set(list(hostssorted)))) 

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
#    print(servicename)
#    print(envhost) 
    searchurl = envhost+SEARCH+servicename+"$"
    x = getInfo(servicename,options.environment)

    if al:
        print(searchurl)
        searchinchredirector(searchurl, servicename, x)

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
