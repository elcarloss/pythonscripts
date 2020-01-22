#!/usr/bin/env python

import requests
import xmltodict
import socket
import struct
import time

class RedirectorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class redir(object):

    def __init__(self, environment, servicename):
        ENVIRONMENT_SDEV  = "dev"
        ENVIRONMENT_STEST = "test"
        ENVIRONMENT_SCERT = "cert"
        ENVIRONMENT_PROD  = "prod"

        if environment == ENVIRONMENT_SDEV:
            self.url = 'http://internal.gosredirector.online.ea.com:42125'
        elif environment == ENVIRONMENT_STEST:
            self.url = 'http://internal.gosredirector.stest.ea.com:42125'
        elif environment == ENVIRONMENT_SCERT:
            self.url = 'http://internal.gosredirector.scert.ea.com:42125'
        elif environment == ENVIRONMENT_PROD:
            self.url = 'http://tools.internal.gosredirector.ea.com:42125'
        else:
            raise RedirectorError("Unknown environment {0}".format(
            environment ) )

        self._request(servicename)

    def _request(self, servicename):
        uri = '{0}/redirector/getServerList?name={1}$'.format(self.url,
        servicename)
        try:
            start = time.time()
            req = requests.get(uri, timeout=5)
            end = time.time()
            self.data = xmltodict.parse(req.text)
            self.time = "Request took %f ms" % ((end - start) * 1000.0)
        except requests.exceptions.ConnectTimeout as e:
            raise RedirectorError('Request to {0} had a timeout of 5'\
            'sec'.format(uri))

    def get_buildtarget(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['buildtarget']

    def get_buildtime(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['buildtime']

    def get_depotlocation(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['depotlocation']

    def get_buildlocation(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['buildlocation']

    def get_blazename(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['name']

    def get_servicenames(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['servicenames']

    def get_blazeversion(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['version']

    def get_platform(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['platform']

    def get_defaultdnsaddress(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        dns = int(serverinfodata['defaultdnsaddress'])
        return socket.inet_ntoa( struct.pack( '!L', dns) )

    def get_slaves(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        instances = serverinfodata['instances']['serverinstance']
        slaves = {}
        if type(instances) is list:
            for i in instances:
                slaves[i['instancename']]=[]
                #print i['instancename']
                endpoint = i['endpoints']['serverendpointinfo']
                ips = set()
                ports = set()
                for j in endpoint:
                    address = j['addresses']['serveraddressinfo']
                    if type(address) is list:
                        for g in address:
                            if 'ip' in g['address']['valu']:
                                ip = socket.inet_ntoa( struct.pack( '!L', int(g['address']['valu']['ip'])))
                                port = g['address']['valu']['port']
                                #print ip, port
                                ips.add(ip)
                    else:
                        if 'ip' in address['address']['valu']:
                            ip = socket.inet_ntoa( struct.pack( '!L', int(address['address']['valu']['ip'])))
                            port = address['address']['valu']['port']
                            #print ip, port
                            ips.add(ip)
                #print ips, ports
                slaves[i['instancename']].append(i['inservice'])
                slaves[i['instancename']].append(ips)
        else:
            slaves[instances['instancename']]=[]
            endpoint = instances['endpoints']['serverendpointinfo']
            ips = set()
            ports = set()
            for j in endpoint:
                address = j['addresses']['serveraddressinfo']
                if type(address) is list:
                    for g in address:
                        if 'ip' in g['address']['valu']:
                            ip = socket.inet_ntoa( struct.pack( '!L',int(g['address']['valu']['ip'])))
                            port = g['address']['valu']['port']
                            ips.add(ip)
                else:
                    if 'ip' in address['address']['valu']:
                        ip = socket.inet_ntoa( struct.pack( '!L',int(address['address']['valu']['ip'])))
                        port = address['address']['valu']['port']
                        ips.add(ip)
            slaves[instances['instancename']].append(instances['inservice'])
            slaves[instances['instancename']].append(ips)
        return slaves

    def get_masters(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        masterinstances = serverinfodata['masterinstance']
        currenworkdir = serverinfodata['masterinstance']['currentworkingdirectory']
        masters = {}
        masters[masterinstances['instancename']] = []
        ips = set()
        for i in masterinstances['endpoints']['serverendpointinfo']:
            address = i['addresses']['serveraddressinfo']
            ips.add(socket.inet_ntoa( struct.pack( '!L', int(address['address']['valu']['ip']))))
        masters[masterinstances['instancename']].append(masterinstances['inservice'])
        masters[masterinstances['instancename']].append(ips)
        return masters

    def get_auxmasters(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        auxmasters=serverinfodata['auxmasters']['serverinstance']
        aux_masters = {}
        for i in auxmasters:
            aux_masters[i['instancename']]=[]
            #print i['instancename']
            endpoint = i['endpoints']['serverendpointinfo']
            ips = set()
            ports = set()
            for j in endpoint:
                address = j['addresses']['serveraddressinfo']
                if type(address) is list:
                    for g in address:
                        if 'ip' in g['address']['valu']:
                            ip = socket.inet_ntoa( struct.pack( '!L', int(g['address']['valu']['ip'])))
                            port = g['address']['valu']['port']
                            #print ip, port
                            ips.add(ip)
                else:
                    if 'ip' in address['address']['valu']:
                        ip = socket.inet_ntoa( struct.pack( '!L', int(address['address']['valu']['ip'])))
                        port = address['address']['valu']['port']
                        #print ip, port
                        ips.add(ip)
            #print ips, ports
            aux_masters[i['instancename']].append(i['inservice'])
            aux_masters[i['instancename']].append(ips)
        return aux_masters

    def get_auxslaves(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        auxslaves = serverinfodata['auxslaves']['serverinstance']
        aux_slaves = {}
        for i in auxslaves:
            aux_slaves[i['instancename']]=[]
            #print i['instancename']
            endpoint = i['endpoints']['serverendpointinfo']
            ips = set()
            ports = set()
            for j in endpoint:
                address = j['addresses']['serveraddressinfo']
                if type(address) is list:
                    for g in address:
                        if 'ip' in g['address']['valu']:
                            ip = socket.inet_ntoa( struct.pack( '!L', int(g['address']['valu']['ip'])))
                            port = g['address']['valu']['port']
                            #print ip, port
                            ips.add(ip)
                else:
                    if 'ip' in address['address']['valu']:
                        ip = socket.inet_ntoa( struct.pack( '!L', int(address['address']['valu']['ip'])))
                        port = address['address']['valu']['port']
                        #print ip, port
                        ips.add(ip)
            #print ips, ports
            aux_slaves[i['instancename']].append(i['inservice'])
            aux_slaves[i['instancename']].append(ips)
        return aux_slaves

    def get_cwd(self):
        serverinfodata = self.data['serverlist']['servers']['serverinfodata']
        return serverinfodata['masterinstance']['currentworkingdirectory']
