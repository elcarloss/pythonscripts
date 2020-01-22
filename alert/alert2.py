import json
import urllib3
import xmltodict
import io
import os
import sys
import smtplib
import socket
import struct
from yaml import load, dump
from deepdiff import DeepDiff
from time import gmtime, strftime
from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from slacknotification import downnotification, upnotification
PATH = os.environ['HOME']+'/pyvirtual/scripts/Classes/Redirector'
sys.path.insert(0, PATH)
from redirclass import redir, RedirectorError



TITLESALERTS = {
    'fifa-2017-ps4$':'prod',
    'madden-2019-ps4$':'prod',
    'madden-2019-xone$':'prod',
    'fifa-2016-ps4$':'prod',
    'fifa-2016-ps3$':'prod',
    'fifa-2016-xone':'prod',
    'fifa-2015-ps3':'prod',
    'fifa-2016-xbl2':'prod',
    'fifa-2015-ps4':'prod',
    'fifa-2016-xbl2':'prod',
    'fifa-2017-xone$':'prod',
    'fifa-2017-xbl2$':'prod',
    'fifa-2017-pc$':'prod',
    'fifa-2017-ps3$':'prod',
    'battlefield-1-ps4$':'prod',
    'battlefield-1-pc$':'prod',
    'battlefield-1-xone$':'prod',
    'nba-2016-ps4':'prod',
    'masseffect-4-xone':'prod',
    'masseffect-4-ps4':'prod',
    'masseffect-4-pc':'prod',
    'nba-2016-xone':'prod',
    'madden-2017-ps4$':'prod',
    'madden-2017-xone$':'prod',
    'madden-2014-xbl2$':'prod',
    'battlefield-4-ps4':'prod',
    'battlefield-3-ps3':'prod',
    'battlefield-3-xbl2':'prod',
    'battlefield-4-xone':'prod',
#    'battlefield-4-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-ps3',
#    'battlefield-4-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-xbl2',
#    'battlefield-havana-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps3',
#    'battlefield-havana-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps4',
#    'battlefield-havana-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xbl2',
#    'battlefield-havana-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xone',
    'plantsvszombies-gw-pc':'prod',
    'plantsvszombies-gw-ps3':'prod',
    'plantsvszombies-gw-ps4':'prod',
    'plantsvszombies-gw-xbl2':'prod',
    'plantsvszombies-gw-xone':'prod',
    'plantsvszombies-gw2-pc$':'prod',
    'plantsvszombies-gw2-ps4$':'prod',
    'plantsvszombies-gw2-xone$':'prod',
    'battlefront-1-pc$':'prod',
    'battlefront-1-ps4$':'prod',
    'battlefront-1-xone$':'prod',
#    'ufc-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-ps4',
#    'ufc-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-xone',
    'dragonage-3-pc':'prod',
    'nfs-2016-ps4':'prod',
    'nfs-2016-xone':'prod',
    'nfs-2016-pc':'prod',
    'nfs-2018-pc$':'prod',
    'nfs-2018-xone$':'prod',
    'nfs-2018-ps4$':'prod',
#    'fifa-2018-ps4-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4-beta$',
#    'fifa-2018-xone-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone-beta$',
#    'nba-2018-xone-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-xone-demo$',
#    'nba-2018-ps4-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-ps4-demo$',
    'nhl-2017-xone':'prod',
    'nhl-2017-ps4':'prod',
#    'madden-2018-xone-eaaccess':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-xone-eaaccess$',
    'madden-2018-xone$':'prod',
    'madden-2018-ps4$':'prod',
    'nba-2018-xone$':'prod',
    'nhl-2018-ps4$':'prod',
    'nhl-2018-xone$':'prod',
#    'nhl-2019-xone-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2019-xone-beta$',
#    'nhl-2019-ps4-beta':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2019-ps4-beta$',


#    'fifa-2018-pc-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-pc-demo$',
#    'fifa-2018-xone-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone-demo$',
#    'fifa-2018-ps4-demo':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4-demo$',
    'battlefield-1-ps4$':'prod',
    'battlefield-1-xone$':'prod',
    'fifa-2018-nx$':'prod',
    'fifa-2018-xone$':'prod',
    'fifa-2018-ps4$':'prod',
    'fifa-2018-pc$':'prod',
    'madden-2016-ps4':'prod',
    'madden-2016-xone':'prod',
    'madden-2016-xbl2':'prod',
    'battlefront-2-pc':'prod',
    'battlefront-2-ps4$':'prod',
#    'jgutierrez-sandbox-pc':'http://internal.gosredirector.stest.ea.com:42125/redirector/getServerList?name=jgutierrez-sandbox-pc$',
    'burnout-paradise-ps4':'prod',
    'burnout-paradise-xone':'prod',
    'awayout-1-ps4':'prod',
    'awayout-1-xone':'prod',
#    'battlefield-casablanca-pc':'http://internal.gosredirector.stest.ea.com:42125/redirector/getServerList?name=battlefield-casablanca-pc$',
#    'battlefield-casablanca-ps4':'http://internal.gosredirector.stest.ea.com:42125/redirector/getServerList?name=battlefield-casablanca-ps4$',
#    'battlefield-casablanca-xone':'http://internal.gosredirector.stest.ea.com:42125/redirector/getServerList?name=battlefield-casablanca-xone$',
    'battlefront-2-xone$':'prod'



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
    msg["From"] = "InternalL2@alerts.ea.com"
#    msg["To"] = "GS-L2Operations@ea.com,alarcon78@gmail.com"
#    msg["To"] = "GS-L2Operations@ea.com"
    msg["To"] = "calarcon@contractor.ea.com"
    msg["Subject"] = "!!!!!!!! ALERT OF CHANGE IN INSTANCE STATUS !!!!!!!!"
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
    p.communicate(msg.as_string())


try:
    to_unicode = unicode
except NameError:
    to_unicode = str

with open('instances5.json') as data_file:
    data_loaded = load(data_file)

con = 0
instancesdct = {}
print "Processing ....."
for x in TITLESALERTS:
    redirector = redir(TITLESALERTS[x], x)
    lstinstances2 = []
    titledictv2 = {}
    lstinstances2.append(redirector.get_instanceslist())
    lstinstances2.append(list(redirector.get_masterinfo()))
    
    instancesdct.update({TITLESALERTS.keys()[con]:lstinstances2})
    con += 1
    print(x, TITLESALERTS[x])
print("Monitored titles: ", con)
#print('--------------------DATA LOADED----------------------')
#print(data_loaded)
#print('-------------------INSTANCES DCT---------------------')
#print(instancesdct)
difes = DeepDiff(instancesdct, data_loaded, ignore_order=True)

#print(difes)
if difes.keys():
    print("Existen Diferencias")
    with io.open('instances5.json', 'w', encoding='utf8') as outfile:
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
#    resumenup = {}
#    resumendown = {}
#    if 'iterable_item_added' in difes:
#        for k,v in difes['iterable_item_added'].iteritems():
#            b = k.strip("root['")
#            c = b.translate(None, '][}{"@\=>:')
#            d = c[:-2]
#            if d in resumendown:
#                resumendown[d].append(v[0])
#            else:
#                resumendown[d]=[v[0]]
#    if 'iterable_item_removed' in difes:
#        for k,v in difes['iterable_item_removed'].iteritems():
#            b = k.strip("root['")
#            c = b.translate(None, '][}{"@\=>:')
#            d = c[:-2]
#            if d in resumenup:
#                resumenup[d].append(v[0])
#            else:
#                resumenup[d]=[v[0]]
#    if resumenup:
#        for l,b in resumenup.iteritems():
#            upnotification(l, '\n'.join(b))
#    if resumendown:
#        for l,b in resumendown.iteritems():
#            downnotification(l, '\n'.join(b))
			
else:
   pass
   print"No changes"
      # print [len(v) for k,v in instancesdct.iteritems()]
