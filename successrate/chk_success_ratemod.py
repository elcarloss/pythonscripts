#!/usr/bin/python2.7

"""
Monitoring alert to verify if the matchmaking success rate is ok.
"""

import sys
import requests
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK


def getendpoints(urldataf):
    """
    Give format to url data
    """
    if urldataf != None and "datapoints" in urldataf[0].keys():
        try:
            lstendpoints = []
            endpoint1 = str(urldataf[0]["datapoints"][0][0])
            endpoint2 = str(urldataf[0]["datapoints"][1][0]).translate(None,"'")
            endpoint3 = str(urldataf[0]["datapoints"][2][0]).translate(None,"'")
            lstendpoints.append(endpoint1)
            lstendpoints.append(endpoint2)
            lstendpoints.append(endpoint3)
            print lstendpoints
            return lstendpoints
        except Exception as e:
            plugin_exit(STATUS_UNK, "Error in URL Data", e)
    else:
        plugin_exit(STATUS_UNK, "No data on URL", '')

def fetch(Service,Timeout):

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

    #request = urllib3.PoolManager(retries=False)
    try:
        response = requests.get(url, timeout=Timeout)
        return response.json()
    except ValueError as e:
        plugin_exit(STATUS_UNK, "Can't connect to graphite URL: Please check service name", e)
    except Exception as e:
        plugin_exit(STATUS_UNK, "Can't connect to URL", e)

if len(sys.argv) < 3:
    if len(sys.argv) == 1:
        plugin_exit(STATUS_UNK, 'You must specify a servicename', '')
    if len(sys.argv) == 2:
        plugin_exit(STATUS_UNK, 'You must specify the timeout', '')

SERVICE = sys.argv[1]
try:
    TIMEOUT = float(sys.argv[2])
except ValueError as e:
    plugin_exit(STATUS_UNK, "Argument for timeout must be float", e)
RESPONSE = fetch(SERVICE,TIMEOUT)
URLDATA = RESPONSE
ENDPOINTDATA = getendpoints(URLDATA)

if '100.0' not in ENDPOINTDATA:
    if not all(x == ENDPOINTDATA[0] for x in ENDPOINTDATA):
        plugin_exit(STATUS_OK, 'Success Rate is ok', '')
    elif "None" in ENDPOINTDATA:
        plugin_exit(STATUS_WARN, 'Success Rate is flat with None Values', '')
    elif '0.0' not in ENDPOINTDATA:
        plugin_exit(STATUS_WARN, 'Success Rate is flat', '')
    else:
        plugin_exit(STATUS_CRIT, 'Success Rate is 0', '')
