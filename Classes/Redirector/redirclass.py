#!/usr/bin/env python
"""Redirector Class to get all info"""

import socket
import struct
import xml.etree.ElementTree as etree
import time
import requests

class RedirectorError(Exception):
    """Redir class to show excetions"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class redir(object):
    """Class to get all info from redirector"""

    def __init__(self, environment, servicename):
        ENVIRONMENT_SDEV = "dev"
        ENVIRONMENT_STEST = "test"
        ENVIRONMENT_SCERT = "cert"
        ENVIRONMENT_PROD = "prod"

        if environment == ENVIRONMENT_SDEV:
            self.url = 'http://internal.gosredirector.online.ea.com:42125'
        elif environment == ENVIRONMENT_STEST:
            self.url = 'http://internal.gosredirector.stest.ea.com:42125'
        elif environment == ENVIRONMENT_SCERT:
            self.url = 'http://internal.gosredirector.scert.ea.com:42125'
        elif environment == ENVIRONMENT_PROD:
            self.url = 'http://tools.internal.gosredirector.ea.com:42125'
        else:
            raise RedirectorError("Unknown environment {0}".format(environment))

        self._request(servicename)

    def _request(self, servicename):
        uri = '{0}/redirector/getServerList?name={1}$'.format(self.url, servicename)
        try:
            start = time.time()
            req = requests.get(uri, timeout=5)
            end = time.time()
            self.data = etree.fromstring(req.content)
            self.time = "Request took %f ms" % ((end - start) * 1000.0)
        except requests.exceptions.ConnectTimeout as e:
            raise RedirectorError('Request to {0} had a timeout of 5 sec'.format(uri))

    def get_buildtarget(self):
        """Method to get the buildtarget"""
        return self.data.findall('.//buildtarget')[0].text

    def get_buildtime(self):
        """Method to get the build time"""
        return self.data.findall('.//buildtime')[0].text

    def get_configversion(self):
        """Method to get the config version"""
        return self.data.findall('.//configversion')[0].text

    def get_depotlocation(self):
        """Method to get the depot location"""
        return self.data.findall('.//depotlocation')[0].text

    def get_buildlocation(self):
        """Method to get the buil location"""
        return self.data.findall('.//buildlocation')[0].text

    def get_blazename(self):
        """Method to get the blaze name"""
        return self.data.findall('.//name')[0].text

    def get_servicenames(self):
        """Method to get the alternative servicenames"""
        return self.data.findall('.//servicenames')

    def get_defaultserviceid(self):
        """Method to get the default service id"""
        return self.data.findall('.//defaultserviceid')[0].text

    def get_blazeversion(self):
        """Method to get the blaze version"""
        return self.data.findall('.//version')[0].text

    def get_platform(self):
        """Method to get the platform"""
        return self.data.findall('.//platform')[0].text

    def get_defaultdnsaddress(self):
        """Method to get the default dns address"""
        return self.data.findall('.//defaultdnsaddress')[0].text

    def get_instanceslist(self):
        """
        Method to get all instances names, inservice status and host decimal ip, except the info
        form the configMaster
        """
        allinstances = []
        for serverinstance in self.data.findall('.//serverinstance'):
            instanceinfo = []
            instancename = serverinstance.find('instancename').text
            inservice = serverinstance.find('inservice').text
            ipnum = serverinstance.findall('.//valu')[0].find('ip').text
            ip = socket.inet_ntoa(struct.pack('!L', int(ipnum)))
            instanceinfo.extend([instancename, inservice, ip])
            allinstances.append(instanceinfo)
        return allinstances

    def get_instanceslistwithports(self):
        pass

    def get_masterinfo(self):
        """Method to get the configMaster info"""
        instancename = self.data.findall('.//masterinstance')[0].find('instancename').text
        inservice = self.data.findall('.//masterinstance')[0].find('inservice').text
        ipnum = self.data.findall('.//masterinstance//valu')[0].find('ip').text
        ip = socket.inet_ntoa(struct.pack('!L', int(ipnum)))
        return instancename, inservice, ip

    def get_cwd(self):
        """Method to get the current working directory"""
        return self.data.findall('.//masterinstance')[0].find('currentworkingdirectory').text
