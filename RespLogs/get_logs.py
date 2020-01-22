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
import paramiko
import zipfile 
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

    statuslst = []
    allinstances = redirector.get_instanceslistwithports()

    if allinstances == None:
        print("Servicename Not exists")
        sys.exit()
    insta = []
    box_instance = []
    dict_instances = []
    for x in allinstances:
        if "coreSlave" in x[0]:
            insta.append(x[0])
            insta.append(socket.getfqdn(x[2]))
            insta.append(x[3])
            if len(dict_instances) == 0:
                dict_instances = {(socket.getfqdn(x[2])) : [(x[0])]}
            else: 
                if (socket.getfqdn(x[2])) in dict_instances:
                    dict_instances[socket.getfqdn(x[2])].append(x[0])
                else:
                    dict_instances.update({(socket.getfqdn(x[2])) : [(x[0])]})

#    print("Diccionario: ", dict_instances)                
    searchurldata = 'http://'+ insta[1]+':'+insta[2]+GETSTATUS
    logdirv = searchlogdir(searchurldata)
    if logdirv == "/app/log":
        cwd = redirector.get_cwd()
        logdir = cwd.split("/",5)
        ruta = "/"+logdir[1]+"/"+logdir[2]+"/"+logdir[3]+"/"+logdir[4]+"/log"    
        logdirv = ruta
        print("Logdirv :", logdirv)      

    return(logdirv, insta, dict_instances)



def main(argv):
    """
    Main function of the script.
    """
    os.system('clear')
    print("Deleting old logs files in the logs directory...")
    cur_path = os.getcwd()
    log_local_dir = cur_path + "/logs/"
    print("Current directory is: ", log_local_dir)
    for filename in os.listdir(log_local_dir):
        if filename.endswith('.log'):
            os.unlink(log_local_dir+filename)
    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')

    parser.add_option('-p', '--parameter', dest='parameter',
                      help='parameters like starting and finish hour to check in the logs, for example -t ERR -b 2019/05/28-00:00 -f 2019/05/28-03:30 --total -F logs/')

    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment, None)
    servicename = options.servicename or None
    parameters = options.parameter or None

    if not all([envhost, servicename]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, instancesredir.py -e <environment> -s <servicename>', "")

    searchurl = envhost+SEARCH+servicename+"$"
    enviro = options.environment
    instances = []
    log_dir, instances, dict_instances  = searchredirector2(searchurl, servicename, enviro)
    remotefilepath = log_dir + '/'
    localfilepath = '/home/calarcon/pyvirtual/scripts/Logs/logs/'
    print("Downloading "+ servicename + " blaze logs ...")
    blaze_file = 'blaze_'+instances[0]+'.log'
    blaze_host = instances[1]
    ssh_client=paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sessions = "_usersessions.log"
    for box in dict_instances:
        conta = 0
        print("===============================================================================")
        print("From the box: ", box)
        print("===============================================================================")
        for ins in dict_instances[box]:
            if conta > 1:
                break
            ssh_client.connect(box)
            blaze_file = 'blaze_'+ins+'.log'
            file_local = localfilepath + blaze_file
            file_remote = remotefilepath + blaze_file
            blaze_file_sessions = 'blaze_'+ins+sessions
            file_local_sessions = localfilepath + blaze_file_sessions
            file_remote_sessions = remotefilepath + blaze_file_sessions
            print("Downloading ", blaze_file, blaze_file_sessions)
            sftp = ssh_client.open_sftp()
            sftp.get(file_remote, file_local)
            sftp.get(file_remote_sessions, file_local_sessions)
            conta +=1
    sftp.close()
    ssh_client.close()



    print ("The logs has been downloaded to the logs directory")

	

if __name__ == "__main__":
    main(sys.argv[1:])
