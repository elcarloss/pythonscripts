#!/usr/bin/python2.7
import sys
from lxml import etree
import os
import requests
from StringIO import StringIO
from gzip import GzipFile
import zlib
import math
import socket
import struct
import nagios
import time

URL = 'http://gosprodfeapp198.abn-iad.ea.com:42131/redirector/getServerList?name=%s'

global timeflag
global starttime

def fetch(uri):
    ''' Fetch a URL '''
    try:
        response = requests.get(uri, timeout=5)
    except requests.exceptions.RequestException as err:
        nagios.plugin_exit(nagios.STATUS_UNK, "Can't connect to URL %s; Reason: %s" % (uri, err), '')
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
    timepassed = time.time() - starttime
    if timepassed > timeflag:
        nagios.plugin_exit(nagios.STATUS_WARN, 'Excedeed time %i, finishing script' % timepassed)
    addressinfos = instance.xpath('./endpoints/serverendpointinfo')
#    global expected_bindtype
    for addressinfo in addressinfos:
        channel = addressinfo.xpath('./channel/text()')[0]
        decoder = addressinfo.xpath('./decoder/text()')[0]
        encoder = addressinfo.xpath('./encoder/text()')[0]
        protocol = addressinfo.xpath('./protocol/text()')[0]
        bindtype = addressinfo.xpath('./bindtype/text()')[0]


        if channel == 'tcp' and decoder == 'http' and encoder == 'xml2' and protocol == 'httpxml':
            addresses = addressinfo.xpath('./addresses/serveraddressinfo')
            for address in addresses:
                if address.xpath('./type/text()')[0] == '0' and bindtype == expected_bindtype:
                    ip = socket.inet_ntoa(struct.pack('!L', int(address.xpath('./address/valu/ip/text()')[0])))
                    port = address.xpath('./address/valu/port/text()')[0]
                    url = 'http://%s:%s/blazecontroller/getStatus' % (ip, port)
                    response = fetch(url)
                    root = etree.fromstring(response)
                    load = 0
                    dsload = 0
                    try:
                        load = int(root.xpath("/serverstatus/components/componentstatus/info/entry[@key='GaugeUS_CLIENT_TYPE_GAMEPLAY_USER_Slave']/text()")[0])
                    except IndexError:
                        try:
                            load = int(root.xpath("/serverstatus/components/componentstatus/info/entry[@key='GaugeUS_CLIENT_TYPE_CONSOLE_USER_Slave']/text()")[0])
                        except IndexError:
                            try:
                                load = int(root.xpath("/serverstatus/components/componentstatus/info/entry[@key='GaugeUserSessionsSlave']/text()")[0])
                            except IndexError:
                                nagios.plugin_exit(nagios.STATUS_UNK, 'Couldn\'t find UserSession entries, try a different bindtype value.', '')
                    try:
                        dsload = int(root.xpath("/serverstatus/components/componentstatus/info/entry[@key='GaugeUS_CLIENT_TYPE_DEDICATED_SERVER_Slave']/text()")[0])
                    except IndexError:
                        dsload = 0
                    try:
                        slave = root.xpath('/serverstatus/instancename/text()')[0]
                    except IndexError:
                        nagios.plugin_exit(nagios.STATUS_UNK, 'Could\'t find instancename.', '')
                    return (slave, load+dsload)
    return 0

if len(sys.argv) < 3:
    nagios.plugin_exit(nagios.STATUS_UNK, 'You must specify at least three parameters separated by spaces: servicename percentage [expected_bindtype] timeout', '')

service = sys.argv[1]
percent = (1.0 * int(sys.argv[2]))/100.0
timeflag = float(sys.argv[3])
expected_bindtype = '1'
starttime = time.time()
response = fetch(URL % service)

root = etree.fromstring(response)
sids = root.xpath('/serverlist/servers/serverinfodata')
for sid in sids:
    snames = sid.xpath('./servicenames/servicenames/text()')
    if service in snames:
        instances = sid.xpath('./instances/serverinstance')
        load = []
        slaves = []
        for instance in instances:
            inservice = instance.xpath('./inservice/text()')[0]
            if inservice == '1':
                try:
                    (slave, l) = get_load(instance, service)
                    load.append(l)
                    slaves.append(slave)
                except TypeError:
                    pass
        sd = stddev(load)
        avg = average(load)
        md = max(load) * percent
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
nagios.plugin_exit(nagios.STATUS_UNK, 'Servicename not found: %s' % service, '')
