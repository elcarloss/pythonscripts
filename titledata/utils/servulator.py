#!/bin/env python2.7

import os
import poller_core.utils.decorators as decorators

from os.path import dirname, abspath
from lxml import objectify
from functools import partial
from poller_core.utils.http_utils import AsyncHTTPRequestQueue
from poller_core.utils.generic_utils import getPollerLogger

ROOT_DIR = dirname(dirname(dirname(abspath(__file__))))
LOG = getPollerLogger()
xsi_type = '{http://www.w3.org/2001/XMLSchema-instance}type'


@decorators.unhandled_exception
def getListOfServulatorInstances(filename):
    servulators = []
    with open(filename, 'r') as f:
        data = f.read()
        f.close()

    data = objectify.fromstring(data)

    for node in data.Objects.iterchildren():
        if node.get(xsi_type) != 'Server':
            continue
        ip = str(node.Ip)
        port = str(node.Port)
        servulators.append(ip + ':' + port)

    return servulators


@decorators.unhandled_exception
def getServulatorServiceNames(process_xml):
    services = {}

    def getServiceName(arguments):
        try:
            environment = arguments.split('-environment=')[1].split(' ')[0]
            servicename = arguments.split('-lobbyname=')[1].split(' ')[0]
            return environment + ':' + servicename
        except IndexError:
            pass

    def getDirtyCastName(runsetId):
        try:
            _, gameName, platform, _ = runsetId.split('/')[1].split('.', 3)
            return gameName + '-' + platform
        except:
            pass


    # Parse process list
    for obj in process_xml.Objects.iterchildren():
        if obj.get(xsi_type) == 'ProcessListResult':
            for process in obj.Processes.iterchildren():
                if process.get(xsi_type) != 'Process':
                    continue
                serviceName = getServiceName(str(process.Arguments))

                if serviceName not in services:
                    services[serviceName] = set()
                services[serviceName].add(getDirtyCastName(str(process.RunSetId)))
        elif obj.get(xsi_type) == 'Process':
            serviceName = getServiceName(str(obj.Arguments))

            if serviceName not in services:
                services[serviceName] = set()
            services[serviceName].add(getDirtyCastName(str(obj.RunSetId)))

    return services


def getServulatorMappings():
    httpQueue = AsyncHTTPRequestQueue()
    servulatorEndpoints = set([])
    servulatorMappings = {}
    servulatorPath = ROOT_DIR + '/in/servulator/'
    # 1.x and 13.1.x have conflicting xmls, cron jobs that copy files to the /in directory must take the following file
    # paths into account
    files = ['%s/1.x/%s' % (servulatorPath, fname) for fname in os.listdir(servulatorPath + '1.x/')]
    files.extend(['%s/13.1.x/%s' % (servulatorPath, fname) for fname in os.listdir(servulatorPath + '13.1.x/')])

    def addToServulatorMapping(xml, endpoint):
        if xml is None:
            LOG.warn('data from %s is None' % endpoint)
            return None
        try:
            process_xml = objectify.fromstring(xml)
            mappings = getServulatorServiceNames(process_xml)
            for serviceName, dirtyCastNames in mappings.items():
                if serviceName not in servulatorMappings:
                    servulatorMappings[serviceName] = {
                        "dirtyCastNames": set(),
                        "servulatorInstances": set()
                    }
                servulatorMappings[serviceName]["dirtyCastNames"].update(dirtyCastNames)
                servulatorMappings[serviceName]["servulatorInstances"].add(endpoint)
        except Exception as e:
            LOG.error(e)

    for file in files:
        sv = getListOfServulatorInstances(file)
        for s in sv:
            servulatorEndpoints.add(s)

    for servulator_endpoint in servulatorEndpoints:
        if 'online.ea.com' in servulator_endpoint:
            LOG.warn('skipping %s as we think it isnt accessible' % servulator_endpoint)
            continue
        url = 'http://%s/process/list' % servulator_endpoint
        httpQueue.put(url, 45, partial(addToServulatorMapping, endpoint=servulator_endpoint))

    LOG.info('Processing %s servulator endpoints' % len(servulatorEndpoints))
    httpQueue.closeQueue(900) # 15min timeout to retrieve servulator instances
    LOG.info('Processed all http requests')

    return servulatorMappings
