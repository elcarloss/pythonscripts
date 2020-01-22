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

def fetch(s):

    """
    Obtain the endpoints data from the url variable
    """

    url = "http://eadp.gos.graphite-web.bio-iad.ea.com/render?format=json&target=alias(scale(movingAverage(divideSeries(nonNegativeDerivative(sumSeries(keepLastValue(eadp.gos.blaze.prod.{0}.mmSlave*.matchmaker.status.%7BScenario%2C%7DMMTotalMatchmakingSessionSuccess)))%2C%20nonNegativeDerivative(sumSeries(keepLastValue(eadp.gos.blaze.prod.{0}.mmSlave*.matchmaker.status.%7BMMTotalMatchmakingSessionTimeout%2CMMTotalMatchmakingSessionCanceled%2CMMTotalMatchmakingSessionTerminated%2CMMTotalMatchmakingSessionSuccess%2CScenarioMMTotalMatchmakingSessionTimeout%2CScenarioMMTotalMatchmakingSessionCanceled%2CScenarioMMTotalMatchmakingSessionTerminated%2CScenarioMMTotalMatchmakingSessionSuccess%7D))))%2C%202)%2C100)%2C%27success%27)&from=-15minutes&rawData=true".format(s) 
    request = urllib3.PoolManager(retries=False)
#    print url
    try:
        requestdata = request.request('GET', url, timeout=3)
#    except urllib3.exceptions.ConnectTimeoutError:
    except Exception as e:
        plugin_exit(STATUS_UNK, "Can't connect to URL", '')

    return requestdata

if len(sys.argv) < 1:
    plugin_exit(STATUS_UNK, 'You must specify a servicename', '')
service = sys.argv[1]
#service = "madden-2017-xbl2"
response = fetch(service)
urldata = response.data
endpointdata = getendpoints(urldata)

if not '100.0' in endpointdata:
    if not all(x==endpointdata[0] for x in endpointdata):
        if '0.0' in endpointdata and all(x==endpointdata[0] for x in endpointdata):
            plugin_exit(STATUS_CRIT, 'Success Rate is 0', '')
    else:
        if all(x==endpointdata[0] for x in endpointdata) and not 'null' in endpointdata:
            plugin_exit(STATUS_WARN, 'Success Rate is flat', '')

print("The last 3 endpoints are: ",endpointdata)
plugin_exit(STATUS_OK, 'Success Rate is ok', '')
