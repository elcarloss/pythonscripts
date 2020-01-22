#!/usr/bin/python2.7

"""
Monitoring alert to verify if the matchmaking success rate is ok.
"""

import sys
import urllib3
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK


def getendpoints(urldataf):

    """
    Get the endpoints from the url data obtained in fetch function
    """

    lstendpoints = []
    for row in urldataf.splitlines():
        fields = row.split('[')
    endpoint1 = fields[3].split(",")[0].translate(None, "'")
    endpoint2 = fields[4].split(",")[0].translate(None, "'")
    endpoint3 = fields[5].split(",")[0].translate(None, "'")
    lstendpoints.append(endpoint1)
    lstendpoints.append(endpoint2)
    lstendpoints.append(endpoint3)
    return lstendpoints

def fetch(Service):

    """
    Obtain the endpoints data from the url variable
    """

    url = "http://eadp.gos.graphite-web.bio-iad.ea.com/render?format=json&target=alias(scale(\
movingAverage(divideSeries(nonNegativeDerivative(sumSeries(keepLastValue(eadp.gos.blaze.\
prod.{0}.mmSlave*.matchmaker.status.%7BScenario%2C%7DMMTotalMatchmakingSessionSuccess)))\
%2C%20nonNegativeDerivative(sumSeries(keepLastValue(eadp.gos.blaze.prod.{0}.mmSlave*.matchmaker.\
status.%7BMMTotalMatchmakingSessionTimeout%2CMMTotalMatchmakingSessionCanceled%\
2CMMTotalMatchmakingSessionTerminated%2CMMTotalMatchmakingSessionSuccess%\
2CScenarioMMTotalMatchmakingSessionTimeout%2CScenarioMMTotalMatchmakingSessionCanceled%\
2CScenarioMMTotalMatchmakingSessionTerminated%2CScenarioMMTotalMatchmakingSessionSuccess%7D))))\
%2C%202)%2C100)%2C%27success%27)&from=-15minutes&rawData=true".format(Service)
    request = urllib3.PoolManager(retries=False)
    try:
        requestdata = request.request('GET', url, timeout=4)
    except Exception as e:
        plugin_exit(STATUS_UNK, "Can't connect to URL", e)

    return requestdata

if len(sys.argv) < 1:
    plugin_exit(STATUS_UNK, 'You must specify a servicename', '')
SERVICE = sys.argv[1]
RESPONSE = fetch(SERVICE)
URLDATA = RESPONSE.data
ENDPOINTDATA = getendpoints(URLDATA)

if '100.0' not in ENDPOINTDATA:
    if not all(x == ENDPOINTDATA[0] for x in ENDPOINTDATA):
        if '0.0' in ENDPOINTDATA and all(x == ENDPOINTDATA[0] for x in ENDPOINTDATA):
            plugin_exit(STATUS_CRIT, 'Success Rate is 0', '')
    else:
        if all(x == ENDPOINTDATA[0] for x in ENDPOINTDATA) and 'null' not in ENDPOINTDATA:
            plugin_exit(STATUS_WARN, 'Success Rate is flat', '')

plugin_exit(STATUS_OK, 'Success Rate is ok', '')
