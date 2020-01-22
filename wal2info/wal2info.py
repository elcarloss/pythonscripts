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
import sys
import csv
import os
import socket
import struct
from pprint import pprint
from pssh import ParallelSSHClient
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)


BIODUB = ["eadpgsl0237.bio-dub.ea.com", "eadpgsl0238.bio-dub.ea.com", "eadpgsl0239.bio-dub.ea.com", "eadpgsl0240.bio-dub.ea.com"]
EAIAD = ["eadpgsl0248.bio-iad.ea.com", "eadpgsl0249.bio-iad.ea.com", "eadpgsl0250.bio-iad.ea.com", "eadpgsl0251.bio-iad.ea.com"]
BIOIAD = ["eadpgsl0248.bio-iad.ea.com", "eadpgsl0249.bio-iad.ea.com", "eadpgsl0250.bio-iad.ea.com", "eadpgsl0251.bio-iad.ea.com"]
RSP = ["gosprapp439.rspc-lhr.ea.com", "gosprapp440.rspc-lhr.ea.com", "gosprapp443.rspc-lhr.ea.com", "gosprapp444.rspc-lhr.ea.com", "gosprapp447.rspc-lhr.ea.com", "gosprapp448.rspc-lhr.ea.com", "gosprapp451.rspc-lhr.ea.com", "gosprapp452.rspc-lhr.ea.com"]
AMS = ["gosprodfeapp0234.eqx-ams.ea.com", "gosprodfeapp0235.eqx-ams.ea.com", "gosprodfeapp0236.eqx-ams.ea.com"]

PRUEBA = ["gosltapp1079.eqx-ams.ea.com", "gosltapp1080.eqx-ams.ea.com"]

biodubopc = ["biodub", "wal2.tools.gos.bio-dub.ea.com"]
rspopc = ["rsp", "wal2.tools.gos.rs-lhr.ea.com"]
eaiadopc = ["eaiad", "wal2.tools.gos.ea-iad.ea.com"]
bioiadopc = ["eaiad", "wal2.tools.gos.ea-iad.ea.com"]
amsopc = ["ams", "wal2.tools.gos.ea-ams.ea.com"]




def editappkeywal2(vi):
   os.system('clear')
   if vi in amsopc:
       client = ParallelSSHClient(PRUEBA)
       command = "sudo -u tomcat vim /etc/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties"
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")




def searchappkeywal2(env, vi, appk):
#   os.system('clear')
   if vi in rspopc:
       client = ParallelSSHClient(RSP)
       command = "sudo -u tomcat cat /etc/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (appk)
 #      print("El comando a ejecutar es: ",command)
       output = client.run_command(command)     
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")

   if vi in biodubopc:
       client = ParallelSSHClient(BIODUB)
       command = "sudo -u gos-tools cat /opt/gos-tools/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (appk)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")


   if (vi in eaiadopc) or (vi in bioiadopc):
       client = ParallelSSHClient(EAIAD)
       command = "sudo -u gos-tools cat /opt/gos-tools/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (appk)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")

   if vi in amsopc:
       client = ParallelSSHClient(AMS)
       command = "sudo -u tomcat cat /etc/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (appk)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")


def searchrpcwal2(env, vi, rp):
#   os.system('clear')
   if vi in rspopc:
       client = ParallelSSHClient(RSP)
       command = "sudo -u tomcat cat /etc/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/rpcwhitelist/appkey-rpcwhitelist.properties|grep %s" % (rp)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")

   if vi in biodubopc:
       client = ParallelSSHClient(BIODUB)
       command = "sudo -u gos-tools cat /opt/gos-tools/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (rp)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")

   if (vi in eaiadopc) or (vi in bioiadopc):
       client = ParallelSSHClient(EAIAD)
       command = "sudo -u gos-tools cat /opt/gos-tools/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/appkey.properties|grep %s" % (rp)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")

   if vi in amsopc:
       client = ParallelSSHClient(AMS)
       command = "sudo -u tomcat cat /etc/tomcat6/webapps/wal2/WEB-INF/classes/META-INF/appkey/rpcwhitelist/appkey-rpcwhitelist.properties|grep %s" % (rp)
#       print("El comando a ejecutar es: ",command)
       output = client.run_command(command)
       for hos in output:
           for line in output[hos].stdout:
               print("Host %s : %s " % (hos, line))
               print("\n")



if __name__ == "__main__":
    """
    Main function of the script.
    """
    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test, stress')
    parser.add_option('-v', '--vip', dest='vip',
                      help='Vip to check for example wal2.tools.gos.bio-dub.ea.com or region ams, biodub, rs, eaiad, bioiad')
    parser.add_option('-a', '--appkey', dest='appkey',
                      help='appkey to check for example WWW_SOVEREIGN', default=0)
#    parser.add_option('-d', '--edit', dest='edit',
#                      help='Option to edit the appkey files', default=0)
    parser.add_option('-r', '--rpc', dest='rpc', 
                      help='rpc to check for example audit', default=0)
   
    (options, args) = parser.parse_args()

    enviro = options.environment
    vip = options.vip or None
    if not all([enviro, vip]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, wal2info.py -e <environment> -v <vip> -a <appkey> -r <rpc>', "")
    appkey = options.appkey or None
    rpc = options.rpc or None
#    edit = options.edit or None
#    print(servicename)
#    print(envhost) 
#    searchurl = envhost+SEARCH+servicename+"$"
    if appkey:
        searchappkeywal2(enviro, vip, appkey)
    if rpc:
        searchrpcwal2(enviro, vip, rpc)
#    if all[vip, edit]:
#        editappkeywal2(vip)

#    print("Valor de la lista X")
#    pprint.pprint (x)



#If not options has been choosen 
    if (enviro == None and appkey == None and rpc == None):
        os.system("clear")
        print("(----------- NOT VALID OPTIONS HAS BEEN CHOOSEN ----------)")
        print("The sintaxis for this script is:")    
        print("wal2info.py -e <environment> -v <vip> -a <appkey> -r <rpc>")
        print("Where -a 1 -d 1 -r 1 -p 1 and -b 1 are optional parameters")
        print("dev  = dev.wal2.tools.gos.bio-sjc.ea.com")
        print("test = test.wal2.tools.gos.bio-dub.ea.com - ip = 159.153.74.64")
        print("cert = cert.wal2.tools.gos.bio-dub.ea.com - ip = 159.153.74.66")
        print("prod = wal2.tools.gos.ea-iad.ea.com - ips = 10.72.164.58, 10.72.164.106, 10.72.164.107, 10.72.164.108")
        print("prod = wal2.tools.gos.bio-iad.ea.com - ips = 10.72.164.58, 10.72.164.106, 10.72.164.107, 10.72.164.108")
        print("prod = wal2.tools.gos.rs-lhr.ea.com - ips = 10.99.31.19, 10.99.31.20, 10.99.31.24, 10.99.31.25, 10.99.31.29, 10.99.31.30, 10.99.31.34, 10.99.31.35")
        print("prod = wal2.tools.gos.ea-ams.ea.com - ips = 10.128.74.145, 10.128.74.146, 10.128.74.147")
        print("prod = wal2.tools.gos.bio-dub.ea.com - ips = 10.74.213.197, 10.74.213.198, 10.74.213.199, 10.74.213.200")
        print("stress = stest.cts.wal2.tools.gos.ea-ams.ea.com")
