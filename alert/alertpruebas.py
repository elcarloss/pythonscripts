import json
import urllib3
import xmltodict
import io
import os
import smtplib
import socket
import struct
from yaml import load, dump
from deepdiff import DeepDiff
from time import gmtime, strftime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE




TITLESALERTS = {
    'fifa-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-ps4$',
    'fifa-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-ps4$',
    'fifa-2016-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-ps3$',
    'fifa-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xone$',
    'fifa-2015-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2015-ps3$',
    'fifa-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xbl2$',
    'fifa-2015-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2015-ps4$',
    'fifa-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xbl2$',
    'fifa-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-xone$',
    'fifa-2017-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-xbl2$',
    'fifa-2017-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-pc$',
    'fifa-2017-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-ps3$',
    'battlefield-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-ps4$',
    'battlefield-1-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-pc$',
    'battlefield-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-xone$',
    'nba-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-ps4',
    'masseffect-4-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-xone',
    'masseffect-4-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-ps4',
    'masseffect-4-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-pc',
    'nba-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-xone',
    'madden-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2017-ps4',
    'madden-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2017-xone',
    'madden-2014-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2014-xbl2$',
    'battlefield-4-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-ps4',
    'battlefield-3-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-3-ps3',
    'battlefield-3-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-3-xbl2',
    'battlefield-4-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-xone$',
    'battlefield-4-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-ps3',
    'battlefield-4-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-xbl2',
    'battlefield-havana-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps3',
    'battlefield-havana-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps4',
    'battlefield-havana-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xbl2',
    'battlefield-havana-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xone',
    'plantsvszombies-gw-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-pc',
    'plantsvszombies-gw-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-ps3',
    'plantsvszombies-gw-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-ps4',
    'plantsvszombies-gw-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-xbl2',
    'plantsvszombies-gw-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-xone',
    'plantsvszombies-gw2-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-pc',
    'plantsvszombies-gw2-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-ps4',
    'plantsvszombies-gw2-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-xone',
    'battlefront-1-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-pc',
    'battlefront-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-ps4',
    'battlefront-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-xone',
    'ufc-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-ps4',
    'ufc-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-xone',
    'dragonage-3-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=dragonage-3-pc',
    'nfs-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-ps4',
    'nfs-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-xone',
    'nfs-2016-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-pc',
    'nfs-2018-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-pc',
    'nfs-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-xone',
    'nfs-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-ps4',
#    'fifa-2018-ps4-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4-beta$',
#    'fifa-2018-xone-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone-beta$',
#    'nba-2018-xone-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-xone-demo$',
#    'nba-2018-ps4-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-ps4-demo$',
    'nhl-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-ps4$',
    'nhl-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-xone$',
    'nhl-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-ps4$',
#    'madden-2018-xone-eaaccess':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-xone-eaaccess$',
    'madden-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-xone$',
    'madden-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-ps4$',
    'nba-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-xone$',
    'nhl-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-ps4$',
    'nhl-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-xone$',
#    'fifa-2018-pc-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-pc-demo$',
#    'fifa-2018-xone-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone-demo$',
#    'fifa-2018-ps4-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4-demo$',
    'battlefield-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-ps4$',
    'battlefield-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-xone$',
    'fifa-2018-nx':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-nx$',
    'fifa-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone$',
    'fifa-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4$',
    'madden-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-ps4',
    'madden-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-xone',
    'madden-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-xbl2',
    'ufc-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2018-xone',
    'ufc-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2018-ps4',
    'battlefront-2-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-pc',
    'battlefront-2-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-ps4',
    'battlefront-2-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-xone'



    }

BADWORDS = ["iterable_item_added"] 

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


def sendmail(parts):
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    parts.pop(0)
    msgs = ""
    sal3 = ""
    sal = ""
    for y in parts:
       if y == ', ':
           parts.remove(y)
    for h in range(len(parts)):
        if parts[h] == 'iterable_item_added':
            break
        elif h % 3 == 0:
            sal3 = "The title ", parts[h], " has the instance ", parts[h+1], " changed its status (down/up/stalled)\n"
            message = ''.join(sal3)
            sal = ''.join([sal, message])
    msg = MIMEText(sal)
#    print(sal)
    msg["From"] = "noreply@alertas.ea.com"
#    msg["To"] = "GS-L2Operations@ea.com,alarcon78@gmail.com"
    msg["To"] = "GS-L2Operations@ea.com"

#    msg["To"] = "calarcon@contractor.ea.com"
    msg["Subject"] = "!!!!!!!!! ALERT OF CHANGE IN INSTANCE STATUS !!!!!!!!!"
    print("Mensaje a enviar por correo ")
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
    p.communicate(msg.as_string())


try:
    to_unicode = unicode
except NameError:
    to_unicode = str

with open('instances2.json') as data_file:
    data_loaded = load(data_file)

con = 0
instancesdct = {}
print "Processing ....."
for x in TITLESALERTS.values():
    lstinstances2 = []
    titledictv2 = {}
    http2v2 = urllib3.PoolManager(retries=False)
    titlexmlv2 = http2v2.request('GET', x, timeout=3)
    titledictv2 = xmltodict.parse(titlexmlv2.data)
    titlejsonv2 = json.dumps(titledictv2)

    lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['instancename']))
    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance']:
#        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(k[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))))])
        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1])])

    for y in titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']:
#        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(k[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))))])

        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1])])

    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxslaves']['serverinstance']:
#        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(k[1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))))])
        lstinstances2.append([str(y.items()[4][1]), str(y.items()[5][1])])

    instancesdct.update({TITLESALERTS.keys()[con]:lstinstances2})
    con += 1
    print(x)
print("Monitored titles: ", con)
difes = DeepDiff(instancesdct, data_loaded, ignore_order=True)


if difes.keys():
    with io.open('instances2.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(instancesdct,
        indent=4, sort_keys=True,
        separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
    plan = str(difes)
    parts = plan.split("'\'")
    x = 0
    for item in parts:
        parts[x] = parts[x].translate(None, '][}{"@\=>:')
        x = x + 1
    parts = plan.split("'")
    q = 0
    for items in parts:
        parts[q] = parts[q].translate(None, '{:"')
        q = q + 1

    for h in parts:
        if "root" in h:
            parts.remove(h)
        if 'iterable_' in h:
            parts.remove(h)
        if '][' in h:
            parts.remove(h)
        if '}' in h:
            parts.remove(h)
    for q in parts:
        if "root" in q:
            parts.remove(q)
    sendmail(parts)
			
else:
   pass
   print"No changes"
      # print [len(v) for k,v in instancesdct.iteritems()]
