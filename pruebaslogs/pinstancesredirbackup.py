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
import pprint



TITLESALERTS = {
#    'fifa-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-ps4$',
#    'fifa-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-ps4$',
#    'fifa-2016-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-ps3$',
#    'fifa-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xone$',
#    'fifa-2015-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2015-ps3$',
#    'fifa-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xbl2$',
#    'fifa-2015-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2015-ps4$',
#    'fifa-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2016-xbl2$',
#    'fifa-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-xone$',
#    'fifa-2017-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-xbl2$',
#    'fifa-2017-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-pc$',
#    'fifa-2017-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2017-ps3$',
#    'battlefield-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-ps4$',
#    'battlefield-1-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-pc$',
#    'battlefield-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-xone$',
#    'nba-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-ps4',
#    'masseffect-4-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-xone',
#    'masseffect-4-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-ps4',
#    'masseffect-4-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-pc',
#    'nba-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-xone',
#    'madden-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2017-ps4',
#    'madden-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2017-xone',
#    'madden-2014-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2014-xbl2$',
#    'battlefield-4-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-ps4',
#    'battlefield-3-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-3-ps3',
#    'battlefield-3-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-3-xbl2',
#    'battlefield-4-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-xone$',
#    'battlefield-4-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-ps3',
#    'battlefield-4-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-4-xbl2',
#    'battlefield-havana-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps3',
#    'battlefield-havana-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-ps4',
#    'battlefield-havana-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xbl2',
#    'battlefield-havana-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-havana-xone',
#    'plantsvszombies-gw-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-pc',
#    'plantsvszombies-gw-ps3':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-ps3',
#    'plantsvszombies-gw-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-ps4',
#    'plantsvszombies-gw-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-xbl2',
#    'plantsvszombies-gw-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw-xone',
#    'plantsvszombies-gw2-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-pc',
#    'plantsvszombies-gw2-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-ps4',
#    'plantsvszombies-gw2-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=plantsvszombies-gw2-xone',
#    'battlefront-1-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-pc',
#    'battlefront-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-ps4',
#    'battlefront-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-1-xone',
#    'ufc-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-ps4',
#    'ufc-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2017-xone',
#    'dragonage-3-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=dragonage-3-pc',
#    'nfs-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-ps4',
#    'nfs-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-xone',
#    'nfs-2016-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2016-pc',
#    'nfs-2018-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-pc',
#    'nfs-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-xone',
#    'nfs-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nfs-2018-ps4',
#    'nhl-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-ps4$',
#    'nhl-2017-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-xone$',
#    'nhl-2017-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2017-ps4$',
#    'madden-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-xone$',
#    'madden-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2018-ps4$',
#    'nba-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2018-xone$',
#    'nhl-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-ps4$',
#    'nhl-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-xone$',
#    'battlefield-1-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-ps4$',
#    'battlefield-1-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefield-1-xone$',
#    'fifa-2018-nx':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-nx$',
#    'fifa-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-xone$',
#    'fifa-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=fifa-2018-ps4$',
#    'madden-2016-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-ps4',
#    'madden-2016-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-xone',
#    'madden-2016-xbl2':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=madden-2016-xbl2',
#    'ufc-2018-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2018-xone',
#    'ufc-2018-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=ufc-2018-ps4',
#    'battlefront-2-pc':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-pc',
    'battlefront-2-ps4':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-ps4',
    'battlefront-2-xone':'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=battlefront-2-xone'



    }

BADWORDS = ["iterable_item_added"] 

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

#with open('instances2.json') as data_file:
#    data_loaded = load(data_file)

con = 0
instancesdct = {}
print "Processing ....."
for x in TITLESALERTS.values():
    lstinstances2 = []
    cl = []
    lstinstancesauxmasters = []
    lstinstancescoreslaves = []
    lstinstancesauxslaves = []
    titledictv2 = {}
    http2v2 = urllib3.PoolManager(retries=False)
    titlexmlv2 = http2v2.request('GET', x, timeout=3)
    titledictv2 = xmltodict.parse(titlexmlv2.data)
    titlejsonv2 = json.dumps(titledictv2)
    cl.append(str(titledictv2['serverlist']['servers']['serverinfodata']['version']))
    lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['instancename']))
    configmasterinservice=lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['inservice']))
    lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['hostname']))
    lstinstances2.append(int2ip(int(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['endpoints']['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))))    

    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance']:
        lstinstancesauxmasters.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip'])))), int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))])

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

    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxslaves']['serverinstance']:
        lstinstancesauxslaves.append([str(y.items()[4][1]), str(y.items()[5][1]), socket.getfqdn(str(int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip'])))), int2ip(int(y.items()[1][1]['serverendpointinfo'][1]['addresses']['serveraddressinfo']['address']['valu']['ip']))])
    print("Servicename: ", x)
    print("CL: ", cl)
    pprint.pprint(lstinstances2)
    pprint.pprint(lstinstancesauxmasters)
    pprint.pprint(lstinstancescoreslaves)
    pprint.pprint(lstinstancesauxslaves)
    con += 1
print("Monitored titles: ", con)




