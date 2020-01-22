#!/usr/bin/env python

#---------------------------------------------------------------------------------------------------
# Imports
#---------------------------------------------------------------------------------------------------

# Standard
#---------------------------------------------------------------------------------------------------
import ConfigParser
import json
import os
import socket
import warnings

# 3rd Party
#---------------------------------------------------------------------------------------------------
import enum
import requests

#---------------------------------------------------------------------------------------------------
# Constants and Globals
#---------------------------------------------------------------------------------------------------
__pkgname__ = 'portservice'
__version__ = '2.0.0'

#---------------------------------------------------------------------------------------------------
# Errors and Excpetions
#---------------------------------------------------------------------------------------------------
class PASError(Exception): pass
class BadInputError(PASError): pass
class UnauthorizedRequest(PASError): pass
class MissingOrIncorrectHeader(PASError): pass


#---------------------------------------------------------------------------------------------------
# Data Types
#---------------------------------------------------------------------------------------------------
class Environment(enum.Enum):
    DEV    = 'dev'
    TEST   = 'test'
    CERT   = 'cert'
    PROD   = 'prod'

class PortType(enum.Enum):
    NORMAL   = 0
    XLSP_UDP = 1
    XLSP_VDP = 2
    REDIS    = 3

class PortRange(object):
    def __init__(self, porttype, startport, endport, service = None):
        super(PortRange, self).__init__()

        if isinstance(porttype, basestring):
            temp = str(porttype).upper()
            self.porttype = PortType[temp]
        else:
            self.porttype = PortType(porttype)

        self.startport = int(startport)
        self.endport = int(endport)

        if self.startport > self.endport:
            raise ValueError("start port higher than end port")

        self.service = service

    def __len__(self):
        return (self.endport - self.startport) + 1

    def __getitem__(self, key):
        if not isinstance(key, int):
            raise KeyError(key)

        port = self.startport + key
        if port > self.endport:
            raise IndexError("port index out of range")

        return port

    def __iter__(self):
        for port in range(self.startport, self.endport + 1):
            yield port

    def __reversed__(self):
        return reversed([x for x in self])

    def __contains__(self, item):
        port = int(item)
        return self.startport <= port <= self.endport

class PortAssignment(PortRange):
    def __init__(self, service, instancename, hostname, porttype, startport, endport):
        super(PortAssignment, self).__init__(porttype, startport, endport, service)
        self.hostname = hostname
        self.instancename = instancename


#---------------------------------------------------------------------------------------------------
# PAS Utility
#---------------------------------------------------------------------------------------------------
class PortService(object):
    def __init__(self, environment):
        super(PortService, self).__init__()

        basepath = os.path.dirname(__file__)
        configfile = os.path.join( basepath, 'pas.cfg' )

        self.environment = Environment(environment.lower())
        parser = ConfigParser.SafeConfigParser(allow_no_value=True)
        with open(configfile, 'r') as fin:
            parser.readfp(fin)
        
        self._base_url = parser.get(self.environment.value, 'url')
        cafile  = parser.get(self.environment.value, 'cafile')
        if cafile is not None:
            self._cafile = os.path.join(basepath, cafile)
        else:
            self._cafile = None

    def has_service(self, servicename):
        if not isinstance(servicename, str):
            raise ValueError("servicename must be a string")

        resp = self._request('GET', 'services', params={'service': servicename})
        names = [ str(item['servicename']) for item in resp['service'] ]

        return servicename in names

    def add_service(self, servicename):
        if not isinstance(servicename, str):
            raise ValueError("servicename must be a string")

        data = {'servicename': servicename}
        resp = self._request('POST', 'services', data=json.dumps(data))

    def has_host(self, hostname):
        if not isinstance(hostname, str):
            raise ValueError("hostname must be a string")

        resp = self._request('GET', 'hosts', params={'hostname': hostname})
        names = [ str(item['hostname']) for item in resp['host'] ]

        return hostname in names

    def add_host(self, hostname, internalips=None, externalips=None):
        if not isinstance(hostname, str):
            raise ValueError("hostname must be a string")

        data = dict()
        data['hostname'] = hostname

        if (not internalips) and (not externalips):
            raise PASError("must provide at least 1 ip for host")

        if internalips is not None:
            if isinstance(internalips, str):
                internalips = [internalips]

            if not isinstance(internalips, list):
                raise ValueError("internalips must be a string or list of strings")
            elif not all([isinstance(item, str) for item in internalips]):
                raise ValueError("internalips must be a string or list of strings")

            data['internalips'] = {'internalip': internalips}

        if externalips is not None:
            if isinstance(externalips, str):
                externalips = [externalips]

            if not isinstance(externalips, list):
                raise ValueError("externalips must be a string or list of strings")
            elif not all([isinstance(item, str) for item in externalips]):
                raise ValueError("externalips must be a string or list of strings")

            data['externalips'] = {'externalip': externalips}

        resp = self._request('POST', 'hosts', data=json.dumps(data))

    def get_ports(self, service=None, instance=None, hostname=None, numports=None, porttype=None):

        payload = dict()
        if service is not None:
            payload["service"] = service

        if instance is not None:
            payload["instance"] = instance

        if porttype is not None:
            if isinstance(porttype, str):
                porttype = PortType[porttype.upper()]
            else:
                porttype = PortType(porttype)
            payload["porttype"] = porttype.name

        if hostname is not None:
            payload['hostname'] = hostname

        ports = list()
        response = self._request('GET', 'portassignments', params=payload)

        if len(response['portassignment']) == 0:
            # post new port selection if possible
            if (service is not None) and (instance is not None) and (porttype is not None) and (ports is not None):
                del payload['instance']
                payload['instancename'] = instance
                payload['ports'] = numports

                if hostname is None:
                    hostname = socket.gethostname()
                else:
                    del payload['hostname']
                payload['host'] = hostname

                response = self._request('POST', 'portassignments', data=json.dumps(payload))
                assignment = PortAssignment(service = response['service'],
                                          instancename = response['instancename'],
                                          hostname = response['host'],
                                          porttype = response['porttype'],
                                          startport = response['start'],
                                          endport = response['end'])
                ports.append(assignment)
        else:
            for info in response['portassignment']:
                assignment = PortAssignment(service = info['service'],
                                          instancename = info['instancename'],
                                          hostname = info['host'],
                                          porttype = info['porttype'],
                                          startport = info['start'],
                                          endport = info['end'])
                ports.append(assignment)

        return ports

    def _request(self, method, api, **kwargs):

        url = "{}/{}".format(self._base_url, api)

        # enforce our defualt header settings
        headers = kwargs.get('headers', dict())
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        headers['X-CLIENT-ENVIRONMENT'] = self.environment.name

        kwargs['headers'] = headers
        kwargs['verify'] = self._cafile

        try:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                resp = requests.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            raise PASError(e.message)
        else:
            code = resp.status_code
            if code == requests.codes.ok:
                return resp.json()
            else:
                cause = str(resp.json()['cause'])
                if code == 400:
                    raise BadInputError(cause)
                elif code == 401:
                    raise UnauthorizedRequest(cause)
                elif code == 406:
                    raise MissingOrIncorrectHeader(cause)
                else:
                    raise PASError(cause)







