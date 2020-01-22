import sys
from optparse import OptionParser
import urllib3
import urllib2
import sys
import re
import csv
import os
import socket
import struct
import paramiko
from nagios import (
    plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
)
import xml.etree.ElementTree as etree
import time
import requests
PATH = os.environ['HOME']+'/p4/gosops/tools/gos24x7/toolbox/Classes/Redirector'
sys.path.insert(0, PATH)
from redirclass import redir, RedirectorError
sys.path.insert(0, PATH)

ENVIRONMENTS = {'prod': 'http://tools.internal.gosredirector.ea.com:42125',
                'cert': 'http://internal.gosredirector.scert.ea.com:42125',
                'dev': 'http://internal.gosredirector.online.ea.com:42125',
                'test': 'http://internal.gosredirector.stest.ea.com:42125'}
SEARCH = '/redirector/getServerList?name='
GETSTATUS = '/blazecontroller/getStatus'


def findRange(loglines, type_, t1=None, t2=None):
    """Filter log lines with a certain message type and timeframe Message types
    can be, ERR,WARN,INFO,FATAL or ALL which is basically all of them."""
    newarray = []
    if t1 is not None and t2 is not None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct >= t1 and ct <= t2:
                    newarray.append(loglines[x])
            else:
                if ct >= t1 and ct <= t2 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])
    if t1 is not None and t2 is None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct >= t1:
                    newarray.append(loglines[x])
            else:
                if ct >= t1 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])

    if t1 is None and t2 is not None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct <= t2:
                    newarray.append(loglines[x])
            else:
                if ct < t2 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])
    if t1 is None and t2 is None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                newarray.append(loglines[x])
            else:
                if type_ in loglines[x][1]:
                    newarray.append(loglines[x])
    return newarray

def Report(log):
    """Create a report based on certain columns in the array
    and then filter by datetime (precision = minutes)."""
    logstrp = [[] for i in range(len(log))]
    for x in range(len(log)):
        logstrp[x].append(log[x][0][:-7])
        logstrp[x].append(log[x][1])
        logstrp[x].append(log[x][2])
        logstrp[x].append(log[x][3])
        neue = re.sub(r'0x[0-9a-f]+', '', log[x][5])
        logstrp[x].append(neue)
    uniqueList = []
    for x in logstrp:
        if x not in uniqueList:
            uniqueList.append(x)
    for x in uniqueList:
        num = logstrp.count(x)
        print "%s" % num,
        print ' '.join(map(str, x))


def Total(log):
    """Create a report for all loglines discarding the time of the error."""
    logstrp = [[]for i in range(len(log))]
    for x in range(len(log)):
        logstrp[x].append(log[x][1])
        logstrp[x].append(log[x][2])
        logstrp[x].append(log[x][3])
        neue = re.sub(r'0x[0-9a-f]+', '', log[x][5])
        logstrp[x].append(neue)
    uniqueList = []
    for x in logstrp:
        if x not in uniqueList:
            uniqueList.append(x)
    for x in uniqueList:
        num = logstrp.count(x)
        print "%s" %num,
        print ' '.join(map(str, x))

def Unparsed(log):
    for x in log:
        print ' '.join(map(str, x))


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

    con = 0
    nodata = 0
    instancesdct = {}
    instotal = []
    print "Processing ....."
    redirector = redir(env, sername)
    if not redirector.get_servicenames():
        plugin_exit(STATUS_CRIT,\
                   'Servicename Not exists', "")

    blaze = redirector.get_blazeversion()
    blazev = blaze.split(" ")[1]
    blazeversion = blazev.split(".")[0]
    print "Blazeversion: ", blaze
    if int(blazeversion) < 13:
        plugin_exit(STATUS_CRIT,\
                   'Blaze version not supported: < 13', "")

    statuslst = []
    allinstances = redirector.get_instanceslistwithports()

    if allinstances == None:
        plugin_exit(STATUS_CRIT,\
                   'Servicename Not exists', "")

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

    searchurldata = 'http://'+ insta[1]+':'+insta[2]+GETSTATUS
    logdirv = searchlogdir(searchurldata)
    if logdirv == "/app/log":
        cwd = redirector.get_cwd()
        logdir = cwd.split("/",5)
        ruta = "/"+logdir[1]+"/"+logdir[2]+"/"+logdir[3]+"/"+logdir[4]+"/log"    
        logdirv = ruta

    return(logdirv, insta, dict_instances)

def validate_options(options):
    global begin, finish
    if options.file is None:
        plugin_exit(STATUS_CRIT,\
                   'ERROR: Blaze log file missing.\n', "")
    if options.begin is not None:
        try:
            begin = time.strptime(options.begin, '%Y/%m/%d-%H:%M')
        except:
            plugin_exit(STATUS_CRIT,\
                   'ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00', "")
    else:
        begin = None

    if options.finish is not None:
        try:
            finish = time.strptime(options.finish, '%Y/%m/%d-%H:%M')
        except:
            plugin_exit(STATUS_CRIT,\
                   'ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00', "")
    else:
        finish = None
    if begin is not None and finish is not None:
        if begin >= finish:
           plugin_exit(STATUS_CRIT,\
                   'Begin time cannot be later or equal to Finish time', "")

def main(argv):
    """
    Main function of the script, delete old logs in /logs directory, 
    """
    os.system('clear')
    print("Deleting old logs files in the logs directory...")
    cur_path = os.getcwd()

    log_local_dir = cur_path + "/logs/"
    for filename in os.listdir(log_local_dir):
        if filename.endswith('.log'):
            os.unlink(log_local_dir+filename)
    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='environment',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-s', '--servicename', dest='servicename',
                      help='Servicename or title of the game to check, for example fifa-2017-ps4')
    parser.add_option('-t', '--type', dest='type', default='ALL',
                      help='OPTIONAL: Filter by Message Type. i.e FATAL,ERR,WARN,INFO. Default is ALL')
    parser.add_option('-b', '--begin', dest='begin',
                      help='OPTIONAL: Begin Matching Time i.e: 2012/03/25-14:56')
    parser.add_option('-f', '--finish', dest='finish',
                      help='OPTIONAL: End Matching Time i.e: 2012/03/25-14:56')

    (options, args) = parser.parse_args()

    envhost = ENVIRONMENTS.get(options.environment, None)
    servicename = options.servicename or None

    if options.begin is not None:
        try:
            begin = time.strptime(options.begin, '%Y/%m/%d-%H:%M')
        except:
           plugin_exit(STATUS_CRIT,\
                   'ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00', "")
    else:
        begin = None

    if options.finish is not None:
        try:
            finish = time.strptime(options.finish, '%Y/%m/%d-%H:%M')
        except:
           plugin_exit(STATUS_CRIT,\
                   'ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00', "")
    else:
        finish = None
    if begin is not None and finish is not None:
        if begin >= finish:
          plugin_exit(STATUS_CRIT,\
                   'ERROR: The begin date cant be minor than the finish date', "")

    if not all([envhost, servicename, finish]):
        plugin_exit(STATUS_WARN,\
                   'Some parameter is missing, python2.7 ./check_logs.py -e prod -s fifa-2016-ps3 -t ALL -b 2019/06/08-11:20 -f 2019/06/08-11:28', "")
##  Get coreslave instances and boxes, ssh to the coreslave boxes, get two coreslave logs of each box
    searchurl = envhost+SEARCH+servicename+"$"
    enviro = options.environment
    instances = []
    log_dir, instances, dict_instances  = searchredirector2(searchurl, servicename, enviro)
    remotefilepath = log_dir + '/'
    localfilepath = log_local_dir
    print("Downloading " +servicename+ " coreslave blaze logs ...")
    blaze_file = 'blaze_'+instances[0]+'.log'
    blaze_host = instances[1]
    ssh_client=paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sessions = "_usersessions.log"
    for box in dict_instances:
        conta = 0
        print("===============================================================================")
        print("From the box: " +box)
        print("===============================================================================")
        for ins in dict_instances[box]:
            if conta > 1:
                break
            ssh_client.connect(box)
            blaze_file = 'blaze_'+ins+'.log'
            file_local = localfilepath + blaze_file
            log_to_check = file_local
            file_remote = remotefilepath + blaze_file
            blaze_file_sessions = 'blaze_'+ins+sessions
            file_local_sessions = localfilepath + blaze_file_sessions
            file_remote_sessions = remotefilepath + blaze_file_sessions
            print("Downloading " +blaze_file+ " <- and -> " +blaze_file_sessions)
            sftp = ssh_client.open_sftp()
            sftp.get(file_remote, file_local)
            sftp.get(file_remote_sessions, file_local_sessions)
            conta +=1
    sftp.close()
    ssh_client.close()
    print " "
    print "The logs have been downloaded to the logs directory"
    print("===============================================================================")    
    try:
        loglines = [logline.strip().split() for logline in open(log_to_check).readlines()] #Parse log file
    except IOError :
        print "ERROR: Could not open file."
        sys.exit(1)
    try:
        rangedvalues = findRange(loglines, options.type, begin, finish) #Get parsed data by range/type
    except ValueError:
        print "ERROR: Unsupported log format. Recommended logs blaze_slave<n>.log or blaze_coreSlave<n>.log"
        sys.exit(1)

    sys.stderr.write('Totals:\n')
    Total(rangedvalues)

    sys.stderr.write('Unparsed data:\n')
    Unparsed(rangedvalues)
    	

if __name__ == "__main__":
    main(sys.argv[1:])
