#!/usr/bin/python2.7
import sys
from lxml import etree
import requests
import math
import socket
import struct
import nagios
import time

#<07-Dec-2017> <Carlos Alarcon>
#<This is a legacy script>
#<Added a timeout flag parameter>
#<Added a main function and other minor modications, lenght lines and erased not
#used imports lines>
#<The redirector URL was updated to the last VIP>


URL = "http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=%s"

def fetch(uri):
    try:
        response = requests.get(uri, timeout=5)
    except requests.exceptions.RequestException as err:
        nagios.plugin_exit(nagios.STATUS_UNK, "Can't connect to URL %s;"+
                           "Reason: %s" % (uri, err), '')
    data = response.content

    return data

def average(nums):
    return sum(nums) * 1.0 / len(nums)

def stddev(nums):
    avg = average(nums)
    variance = map(lambda x: (x - avg)**2, nums)
    avg_var = average(variance)
    return math.sqrt(avg_var)

def get_load(instance, service):
#    Timeout flag logic
    timepassed = time.time() - starttime
    if timepassed > Timeflag:
        nagios.plugin_exit(nagios.STATUS_WARN, 'Excedeed time %i, finishing'+
                           'script' % timepassed)

    addressinfos = instance.xpath('./endpoints/serverendpointinfo')
    for addressinfo in addressinfos:
        channel = addressinfo.xpath('./channel/text()')[0]
        decoder = addressinfo.xpath('./decoder/text()')[0]
        encoder = addressinfo.xpath('./encoder/text()')[0]
        protocol = addressinfo.xpath('./protocol/text()')[0]
        bindtype = addressinfo.xpath('./bindtype/text()')[0]


        if (channel == 'tcp' and decoder == 'http' and encoder == 'xml2'
                and protocol == 'httpxml'):
            addresses = addressinfo.xpath('./addresses/serveraddressinfo')
            for address in addresses:
                if (address.xpath('./type/text()')[0] == '0'
                        and bindtype == expected_bindtype):
                    ip = socket.inet_ntoa(struct.pack('!L', \
                         int(address.xpath('./address/valu/ip/text()')[0])))
                    port = address.xpath('./address/valu/port/text()')[0]
                    url = 'http://%s:%s/blazecontroller/getStatus' % (ip, port)
                    response = fetch(url)
                    root = etree.fromstring(response)
                    load = 0
                    dsload = 0
                    try:
                        load = int(root.xpath("/serverstatus/components/"+
                                              "componentstatus/info/entry"+
                                              "[@key='GaugeUS_CLIENT_TYPE"+
                                              "_GAMEPLAY_USER_Slave']"+
                                              "/text()")[0])
                    except IndexError:
                        try:
                            load = int(root.xpath("/serverstatus/components"+
                                                  "/componentstatus/info/entry"+
                                                  "[@key='GaugeUS_CLIENT_TYPE_"+
                                                  "CONSOLE_USER_Slave']/text()")[0])
                        except IndexError:
                            try:
                                load = int(root.xpath("/serverstatus/components"+
                                                      "/componentstatus/info/"+
                                                      "entry[@key="+
                                                      "'GaugeUserSessionsSlave']"+
                                                      "/text()")[0])
                            except IndexError:
                                nagios.plugin_exit(nagios.STATUS_UNK, 'Couldn\'t '+
                                                   'find UserSession entries, try '+
                                                   'a different bindtype value.', '')
                    try:
                        dsload = int(root.xpath("/serverstatus/components/"+
                                                "componentstatus/info/entry"+
                                                "[@key='GaugeUS_CLIENT_TYPE_"+
                                                "DEDICATED_SERVER_Slave']"+
                                                "/text()")[0])
                    except IndexError:
                        dsload = 0
                    try:
                        slave = root.xpath('/serverstatus/instancename/text()')[0]
                    except IndexError:
                        nagios.plugin_exit(nagios.STATUS_UNK, 'Could\'t '+
                                           ' find instancename.', '')
                    return (slave, load+dsload)
    return 0


def analysis(resp, servic, perc):
    root = etree.fromstring(resp)
    sids = root.xpath('/serverlist/servers/serverinfodata')
    for sid in sids:
        snames = sid.xpath('./servicenames/servicenames/text()')
        if servic in snames:
            instances = sid.xpath('./instances/serverinstance')
            load = []
            slaves = []
            for instance in instances:
                inservice = instance.xpath('./inservice/text()')[0]
                if inservice == '1':
                    try:
                        (slave, l) = get_load(instance, servic)
                        load.append(l)
                        slaves.append(slave)
                    except TypeError:
                        pass
            sd = stddev(load)
            avg = average(load)
            md = max(load) * perc
            delta = map(lambda x: math.floor(abs(x-avg)-md), load)

            perf = 'Std Dev: %s\nPerc of max: %s\nAvg: %s\nLoad: %s\nDeviation: %s' % (sd, md, avg, load, delta)
            delta_slaves = zip(delta, slaves)
            unbalanced = []
            for x in delta_slaves:
                if x[0] > 0:
                    unbalanced.append(x)
            if len(unbalanced) > 0:
                nagios.plugin_exit(nagios.STATUS_CRIT, 'Balancing issue found: %s' % unbalanced, perf)
            nagios.plugin_exit(nagios.STATUS_OK, 'No balancing issue found', perf)
    nagios.plugin_exit(nagios.STATUS_UNK, 'Servicename not found: %s' % servic, '')
    return 0


""" Added a main function """

def main(argv):
  
    global Timeflag
    global starttime
    global expected_bindtype

    if len(sys.argv) < 3:
        nagios.plugin_exit(nagios.STATUS_UNK, 'You must specify at least ' +
                           'three parameters separated by spaces: '+
                           'servicename percentage timeflag', '')
    try:
        service = sys.argv[1]
    except IndexError:
        nagios.plugin_exit(nagios.STATUS_CRIT, 'Error in First parameter', '')
    try:
        percent = (1.0 * int(sys.argv[2]))/100.0
    except IndexError:
        nagios.plugin_exit(nagios.STATUS_CRIT, 'Error in Second parameter', '')
    try:
        Timeflag = float(sys.argv[3])
    except IndexError:
        nagios.plugin_exit(nagios.STATUS_CRIT, 'Timeout Flag parameter is missing', '')
    expected_bindtype = '1'
    starttime = time.time()
    response = fetch(URL % service)
    processing = analysis(response, service, percent)

if __name__ == "__main__":
    main(sys.argv[1:])
