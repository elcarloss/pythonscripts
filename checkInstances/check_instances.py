#!/usr/bin/python2.7
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# February, 2018

# <22-Feb-2018> <Carlos Alarcon>
# <24-Jun-2019> <Update>
# <Check Instances, cpu % by instance, hostnames, ips, Inservice status, Dedicated Servers, Database, instances number comparison by cfg and redirector> 


"""
Tool to obtain servicename data like, instancenames, host, ip and Inservice Status, Cpu % and CL by instance
Valid only for Blaze versions 3, 13, 14 & 15 titles, not working for services only reacheable by bioware vpn
"""
import string
import sys
import json
import urllib
import urllib2
import json
import sys
import csv
import xmltodict
import os
import socket
import struct
import requests
import copy
import pprint
import xml.etree.ElementTree as etree
import ConfigParser
import getpass
import re
from optparse import OptionParser
from P4 import P4, P4Exception
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)
PATH = os.environ['HOME']+'/p4/gosops/tools/gos24x7/toolbox/Classes/Redirector'
#PATH = os.environ['HOME']+'/pyvirtual/scripts/Classes/Redirector'
sys.path.insert(0, PATH)
from redirclass import redir, RedirectorError
sys.path.insert(0, PATH)
from prettytable import PrettyTable


ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='

HTTP = "http://"
GETSTATUS = "/blazecontroller/getStatus"

def check_current(service, env):
    try:
        current = 0
        if env == "prod":
            url =  "https://eadp.gos.graphite-web.bio-iad.ea.com/render/?format=json&target=eadp.gos.torch.prod.%s.Gameplay_Users&from=-1minutes" % (service)
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            current = data[0].get("datapoints")[0][0]
        elif env == "test":
            url =  "https://eadp.gos.graphite-web.bio-iad.ea.com/render/?format=json&target=eadp.gos.torch.test.%s.Gameplay_Users&from=-1minutes" % (service)
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            current = data[0].get("datapoints")[0][0]
        elif env == "dev":
            url =  "https://eadp.gos.graphite-web.bio-iad.ea.com/render/?format=json&target=eadp.gos.torch.dev.%s.Gameplay_Users&from=-1minutes" % (service)
            response = urllib.urlopen(url)
            data = json.loads(response.read())
            current = data[0].get("datapoints")[0][0]
    except:
        print("Failed getting current user value")
        current = 0
    return current



def filep4sync(branch, platform, env, cfg):
    p4 = P4()
    p4.user = os.environ['P4USER']
    p4.client = os.environ['P4CLIENT']
    p4.charset = "utf8"
    p4.port = "eadp-perforce.rws.ad.ea.com:1777"
#    getpass.getpass('P4 Passwd: ')
    try:
        p4.connect()
##        p4.run('sync','-f',branch+'/bin/server_'+env+'_'+platform+'.cfg')
        p4.run('sync','-f',cfg)
    except P4Exception:
        for e in p4.errors: 
            print e
    finally:
        p4.disconnect()


def fileread(branch, platform, env, cfgfile):
    servercfg={}
    reob = re.compile(r' \d+')
    filea = cfgfile
    filer = os.environ['HOME']+'/p4/'+filea.lstrip('/')
#    print("filea: ", filea)
#    print("filer: ", filer)
    conf = ConfigParser.ConfigParser()
    conf.read(filer)
    for server in conf.sections():
        if 'ea.com' in server:
            totsec = 0
            for runset, insts in conf.items(server):
                if runset == 'runset':
#                    print("totsec :", totsec)
                    nlist = insts.strip().split('\n')
#                    print("nlist: ", nlist)
                    for num in nlist:
#                        print("num :", num)
                        fnumb = reob.findall(num)
#                        print("fnumb :", fnumb)
                        if len(fnumb) != 0:
                            fnum = fnumb[0].translate(None, '" ":')
                        else:     
                            fnum = num.split(":")[1]
#                        print("fnum: ", fnum)
                        totsec = totsec + int(fnum)
            servercfg[server]=totsec
    return servercfg


def getclandInstanceCpu(url, cpuv):
    try:
        req = requests.get(url, timeout=5)
        data = etree.fromstring(req.content)
        for h in data.findall('.//version/version'):
            cl_var = h.text
            cltosend = cl_var.split("#")[1].translate(None, ')" "')
        for i in data.findall('.//fibermanagerstatus/cpuusageforprocesspercent'):
            cputosend = i.text
        return(cltosend, cputosend)
    except Exception:
        return("0", 0)
        

def validateblaze(blazever):
    listblaze = blazever.split(".")
    return listblaze

   

def getInstanceCpuPercent(url):
    try:
        req = requests.get(url, timeout=5)
        data = etree.fromstring(req.content)
        for i in data.findall('.//fibermanagerstatus/cpuusageforprocesspercent'):
            return(i.text)
    except Exception:
        return 0

def getcl(url):
    try:
        reqcl = requests.get(url, timeout=5)
        datacl = etree.fromstring(reqcl.content)
        for i in datacl.findall('.//version/version'):
            cl_var = i.text
        return cl_var.split("#")[1].translate(None, ')" "')
    except Exception:
        return "0"

def getGaugeUsersbySlave(url, blazever):
    blazev = validateblaze(blazever)
#    print("Primer digito: ", blazev[0])
#    print("Cuarto digito: ", blazev[3])
    datos = []
    try:
        reqgauge = requests.get(url, timeout=5)
        datagauge = etree.fromstring(reqgauge.content)   
        if (int(blazev[0]) == 15) and (int(blazev[3]) >= 7):
            for instance in datagauge.findall('.//instancename'):
                if "coreSlave" in instance.text:
                    for item in datagauge.findall('.//components/componentstatus/info/entry'):
                        if 'GaugeUserSessionsSlave' == item.attrib.values()[0]:
                            datos.append(item.text)
                            return datos[0]
                else:
                    return "0"
        else:
            for instance in datagauge.findall('.//instancename'):
                if "coreSlave" in instance.text:
#                    print"Si es una instancia coreslave"
                    for item in datagauge.findall('.//components/componentstatus/info/entry'):
#                        print(item.attrib.values(), item.text)
                        if 'GaugeUS_CLIENT_TYPE_GAMEPLAY_USER_Slave' == item.attrib.values()[0]:
#                        if 'GaugeUserSessionsSlave' == item.attrib.values()[0]:
                            datos.append(item.text)
                            return datos[0]
                else:
                    return "0"

        
    except Exception:
       return "0"


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


def getcoreSlavesdedup(allinstances):
    coreinstances = []
    for x in allinstances:
        if "coreSlave" in x[0]:
            x.pop(0)
            x.pop(0)
            x.pop(1)
            coreinstances.append(x)
    if len(coreinstances[0]) == 5:
        for a in coreinstances:
            a.pop(4)
            a.pop(3)
    if len(coreinstances[0]) == 4:
        for b in coreinstances:
            b.pop(3)
    coreslavesdedup = [coreinstances[i] for i in range(len(coreinstances)) if i == 0 or coreinstances[i] != coreinstances[i-1]]
    return coreslavesdedup


def getcoreSlaves(allinstancess):
    coreinstances = []
    for x in allinstancess:
        if "coreSlave" in x[0]:
            coreinstances.append(x)
    return coreinstances

def getinstancesperboxredirector(allinstances, allhosts):
    boxestimes = []
    boxesinstances = []
    for instance in allinstances:
        for host in allhosts:
            if instance[4].count(host):
                boxestimes.append(host)
    for host in allhosts:
        boxesinstances.insert(len(boxesinstances),[host, boxestimes.count(host)])

    return boxesinstances

def getextip(internaldomain):
    intdomain = socket.getfqdn(internaldomain)
    intdom = intdomain.split(".")
    domext = intdom[0] + "." +intdom[2]+ "." + intdom[3]
    try:
        extip = socket.gethostbyname(domext)   
        return extip
    except Exception:
        return " "

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def searchredirector2(schurl, sername, env, titledata, cl, cpu, cfgs, gauge_ins):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str
    indicador = "#"
    sumtotal = 0
    TITLESALERTS = {sername:schurl}
    table = PrettyTable()
    coreSlave_table = PrettyTable()
    instancesbybox_table = PrettyTable()
    redirector = redir(env, sername)
    instances_by_box_cfg = []

    depot = redirector.get_depotlocation()

    branch = depot.split(":")[2]
    platform = sername.split('-')[2]
###    p4file = branch+'/bin/server_'+env+'_'+platform+'.cfg'
    if cfgs:
        p4file = branch+'/bin/'+cfgs
        print(p4file)
    else:
        p4file = branch+'/bin/server_'+env+'_'+platform+'.cfg'

    filep4sync(branch, platform, env, p4file)
    dictcfgfile = fileread(branch, platform, env, p4file)
    for key in sorted(dictcfgfile):
        instances_by_box_cfg.insert(len(instances_by_box_cfg),[key,dictcfgfile[key]])

    nodata = 0
    instotal = []
    extip = []
    print "Processing, please wait ..... "
    current = check_current(sername, env)

    if not redirector.get_servicenames():
        print("Servicename Not exists")
        sys.exit()    

    cwd = redirector.get_cwd()
    cll = redirector.get_blazeversion()
    blazever = cll.split(' ')[1]
    allinstances = redirector.get_instanceslistwithports()
    if allinstances == None:
        print("Servicename Not exists")
        sys.exit()
    for x in range(len(allinstances)):
        allinstances[x].insert(len(allinstances[x]), socket.getfqdn(allinstances[x][2]))
        allinstances[x].insert(len(allinstances[x]), getextip(allinstances[x][2]))
        status = HTTP + allinstances[x][4] + ":" + allinstances[x][3] + GETSTATUS
#        print("Status Page :", status)
        clv = 0    
        print(indicador)
        indicador = indicador + "#"
        if cl and cpu:
            inst_cl_value,inst_cpu_value = getclandInstanceCpu(status, clv)
            allinstances[x].insert(len(allinstances[x]), inst_cl_value)
            allinstances[x].insert(len(allinstances[x]), inst_cpu_value)
            table.field_names = ["Instance", "Serv", "Int IP", "Port", "Dom Name", "Ext IP", "CL", "Cpu %"]
        elif cl:
                 inst_cl_value = getcl(status)
                 table.field_names = ["Instance", "Serv", "Int IP", "Port", "Dom Name", "Ext IP", "CL"]
                 allinstances[x].insert(len(allinstances[x]), inst_cl_value)
#                 usersbySlave = getGaugeUsersbySlave(status)
#                 print("Users by Slave: ", usersbySlave)
        elif cpu:
                 inst_cpu_value = getInstanceCpuPercent(status)
                 table.field_names = ["Instance", "Serv", "Int IP", "Port", "Dom Name", "Ext IP", "Cpu %"]
                 allinstances[x].insert(len(allinstances[x]), inst_cpu_value)
        elif gauge_ins:
                 print("Status Page :", status)
                 inst_gauge_value = getGaugeUsersbySlave(status, blazever)
#                 print(inst_gauge_value)
#                 type(inst_gauge_value)
                 table.field_names = ["Instance", "Serv", "Int IP", "Port", "Dom Name", "Ext IP", "Users by Instance"]
                 if not(inst_gauge_value):
                     inst_gauge_value = 0
                 allinstances[x].insert(len(allinstances[x]), inst_gauge_value)
                 sumtotal = sumtotal + int(inst_gauge_value)
        else:
            table.field_names = ["Instance", "Serv", "Int IP", "Port", "Dom Name", "Ext IP"]
    masterl = list(redirector.get_masterinfo())
    masterl.insert(4, "-----")
    masterl.insert(len(masterl), socket.getfqdn(masterl[2]))
    masterl.insert(len(masterl), "-----")
    if cpu:
        masterl.insert(len(masterl), "-----")
    if cl:
        masterl.insert(len(masterl), "-----")
    if gauge_ins:
        masterl.insert(len(masterl), "-----")
    allinstances.insert(0, masterl)

    set_hosts = []
    for instance in allinstances:
         set_hosts.append(socket.gethostbyaddr(instance[2])[0])         
    allhosts = list(set(set_hosts))
    instancesperboxes_redirector = getinstancesperboxredirector(allinstances, allhosts)

    buildlocation = redirector.get_buildlocation()   
    depot = redirector.get_depotlocation()


#    cl = redirector.get_blazeversion()
    print("\n---------- DETAILED DATA ---------\n\n")
#    print("Blaze Version: ", cl.split(' ')[1])
    print("Blaze Version: ", blazever)
    print("Servicename: ", sername)
    print("Project Title: ", titledata[5])
    print("JiraOTName: ", titledata[6])
    print("Datacenter: ", titledata[7])
    print("CL: ", cll.split(' ')[3])
    print("Depot Location: ", depot)
    print("Build Location: ", buildlocation)
    print("Running in the path: ", cwd)

    print("\n---------- GENERAL INSTANCES INFO --------- ")
    if allinstances:
        for x in allinstances:
##            if x[1] == '0':
##               print("---------------------------------------------------------------------------")
##                print(' '.join(x))
##                print("---------------------------------------------------------------------------")
##            else:
#                print(' '.join(x))
            table.add_row(x)
    else:
        print "There's not instances available" 
#    print ("---------------------------------------------------------------------------------------")

    table.align["Instance"] = "l"
    if cpu:
        table.sortby = "Cpu %"
    else:
        table.sortby = "Int IP"
    if gauge_ins:
        table.sortby = "Dom Name"


    print(table.get_string(title="GS Services Info"))
#    print("\n")
    total = 0
    for key in sorted(dictcfgfile):
#        instances_host_table.add_row("%s: %i" % (key, dictcfgfile[key]))
        total = total + dictcfgfile[key]


    print("\n\033[1;32;40mHosts running in this title: " +str(len(allhosts)))
    if sername and current:
        print("Current Users in the %s game: %i" % (sername,current))
    print("\033[0;37;40m")
    print ("---------------------------------------------------------------------------------------\n")
    allhost = sorted(allhosts)
    instances_by_box_cfg = sorted(instances_by_box_cfg) 
    instancesperboxes_redirector = sorted(instancesperboxes_redirector)
    instancesbybox_table.field_names = ["Host Domain", "Cfg Instances", "Redir Instances"]
    for z in range(len(instances_by_box_cfg)):
        instances_by_box_cfg[z].insert(len(instances_by_box_cfg[z]), instancesperboxes_redirector[z][1])
    for x in instances_by_box_cfg:
        instancesbybox_table.add_row(x)
        
    print ("Ips for coreSlave boxes")

## Table and display of coreslave ips
    coreSlave_table.field_names = ["Internal IP", "Internal Domain", "External IP"]
    coreslavesdedup = getcoreSlavesdedup(allinstances)
      
    for ipcoreslave in coreslavesdedup:
        coreSlave_table.add_row(ipcoreslave)
    coreSlave_table.sortby = "Internal IP" 
    print(coreSlave_table.get_string(title="CoreSlaves IPs"))

    print ("\nComparison between cfg an redirector instances number")
    print(instancesbybox_table.get_string(title="Instances Number by Host"))
    if gauge_ins:
        print("Total coreSlaves instances connections:", sumtotal)

    print("\n\033[1;32;40m Number of instances in the cfg file : "  +str(total))
    print("\033[1;32;40m Number of instances used in this title (in redirector): " +str(len(allinstances)))
    print("\033[1;31;40m")

    if (len)(allinstances) != total:
        print ("\n--------------------------------W A R N I N G-----------------------------------------------------")
        print ("-------------------------------------------------------------------------------------------------")
        print("The number of instances registered in redirector is different than the specified in the .cfg file")
        print ("-------------------------------------------------------------------------------------------------")
        print ("-------------------------------------------------------------------------------------------------\n")
    print("\033[0;37;40m")
   


 
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
                      help='Show instances information, type 1 to activate', default=1)
    parser.add_option('-f', '--cf', dest='cf',
                      help='Introduce a cfg file name', default=0)
    parser.add_option('-c', '--cl', dest='cl',
                      help='Show instances information, type 1 to activate', default=0)
    parser.add_option('-l', '--cpu', dest='cpu',
                      help='Show instances information, type 1 to activate', default=0)
    parser.add_option('-u', '--usu', dest='gauge',
                      help='Show users by instances information, type 1 to activate', default=0)
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
    cpu = options.cpu or None
    cl = options.cl or None
    cfgs = options.cf or None
    gauge_ins = options.gauge or None
    searchurl = envhost+SEARCH+servicename+"$"
    x = getInfo(servicename,options.environment)
    enviro = options.environment
    print("SearchUrl: ",searchurl)
    if al:
        searchredirector2(searchurl, servicename, enviro, x, cl, cpu, cfgs, gauge_ins)

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
