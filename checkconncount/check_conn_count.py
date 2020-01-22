#!/usr/bin/python2.7
import sys
from lxml import etree
import os
from urllib2 import Request, urlopen, URLError
from StringIO import StringIO
from gzip import GzipFile
import zlib
import math
import socket
import struct
import nagios

#URL = 'http://%s/redirector/getServerList?name=%s'
URL = "http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=%s"

#URL = 'http://gosprodfeapp198.abn-iad.ea.com:42131/redirector/getServerList?name=%s'

def fetch(uri, compress=True):
    ''' Fetch a URL, use compression when possible '''
    request = Request(uri)
    if compress:
        request.add_header('Accept-encoding', 'gzip, deflate')
    try:
        response = urlopen(request)
    except URLError, e:
        nagios.plugin_exit(nagios.STATUS_UNK, "Can't connect to URL %s; Reason: %s" % (uri, e.reason), '')

    data = None

    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        f = GzipFile(fileobj=buf)
        data = f.read()
    elif response.info().get('Content-Encoding') == 'deflate':
        data = zlib.decompress(response.read())
    else:
        data = response.read()

    response.close()

    return data

def average(nums):
    return sum(nums) * 1.0 / len(nums)

def stddev(nums):
    avg = average(nums)
    variance = map(lambda x: (x - avg)**2, nums)
    avg_var = average(variance)
    return math.sqrt(avg_var)

def get_load(instance,service):
    addressinfos = instance.xpath('./endpoints/serverendpointinfo')
    global expected_bindtype
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
                    ip = socket.inet_ntoa(struct.pack('!L',int(address.xpath('./address/valu/ip/text()')[0])))
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
                                nagios.plugin_exit(nagios.STATUS_UNK, 'Couldn\'t find UserSession entries, try a different bindtype value.','')
                    try:
                        dsload = int(root.xpath("/serverstatus/components/componentstatus/info/entry[@key='GaugeUS_CLIENT_TYPE_DEDICATED_SERVER_Slave']/text()")[0])
                    except IndexError:
                        dsload = 0
                    slave = root.xpath('/serverstatus/instancename/text()')[0]
                    return (slave, load+dsload)
    return 0

#if len(sys.argv) != 4:
if len(sys.argv) < 3:
    #nagios.plugin_exit(nagios.STATUS_UNK, 'You must specify three parameters separated by spaces: redirector_address:port servicename percentage', '')
    nagios.plugin_exit(nagios.STATUS_UNK, 'You must specify at least two parameters separated by spaces: servicename percentage [expected_bindtype]', '')
#rdir = sys.argv[1]
#service = sys.argv[2]
#percent = (1.0 * int(sys.argv[3]))/100.0

service = sys.argv[1]
percent = (1.0 * int(sys.argv[2]))/100.0
expected_bindtype = '1'
if len(sys.argv) == 4:
    if sys.argv[3] != '1':
        expected_bindtype = sys.argv[3]


#response = fetch(URL % (rdir, service))
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
                #l = int(instance.xpath('./load/text()')[0])
                try:
                    (slave, l) = get_load(instance, service)
                    load.append(l)
                    slaves.append(slave)
                except TypeError:
                    pass
        if len(load) == 0:
            nagios.plugin_exit(nagios.STATUS_UNK, 'No instances of the specified bindtype found. Try a different bindtype value.','')
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


