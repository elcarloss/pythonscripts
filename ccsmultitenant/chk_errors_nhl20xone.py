#4 Errors number below treshold!/usr/bin/python2.7

"""
Monitoring alert to verify if the ccs value from multitenant graphite is minor than treshold.
"""

import sys
import requests
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
from slackclient import SlackClient



TOKEN = "xoxp-3339495132-113342057840-750781819203-bfdb0a703a44ac686e6d18b03bfd0c09"
#TRESHOLD = '10.0'
CHANNEL = "gs_alerts_blaze_log_errors"

def notifyissues(sc):
    msg_issues = "!!ALERT!! nhl-2020-xone Errors in the {database,system,slivers,user,redis} blaze components are incrementing above the treshold !!ALERT!!"
    sc.api_call('chat.postMessage', channel=CHANNEL, text=msg_issues, username='log_error_alert', icon_emoji=':siren:')

def notifyNOissues(sc):
    msg_issues = "All is fine"
#    sc.api_call('chat.postMessage', channel=CHANNEL, text=msg_issues, username='ccs_alert', icon_emoji=':siren:')

def notifyFlatbehavior(sc):
    msg_issues = "!!WARNING!! nhl-2020-xone ERROR rate is flat with None values !!WARNING!!"
    sc.api_call('chat.postMessage', channel=CHANNEL, text=msg_issues, username='error_alert', icon_emoji=':siren:')

def getendpoints(urldataf):
    """
    Give format to url data
    """
    if urldataf != None and "datapoints" in urldataf[0].keys():
        try:
            lstendpoints = []
            leng = len(urldataf[0]["datapoints"])
            endpoint1 = str(urldataf[0]["datapoints"][leng-1][0]).translate(None,"'")
            endpoint2 = str(urldataf[0]["datapoints"][leng-2][0]).translate(None,"'")
            lstendpoints.append(endpoint1)
            lstendpoints.append(endpoint2)
            return lstendpoints
        except Exception as e:
            plugin_exit(STATUS_UNK, "Error in URL Data", e)
    else:
        plugin_exit(STATUS_UNK, "No data on URL", '')

def fetch(Timeout):

    """
    Obtain the endpoints data from the url variable
    """

#    url = "http://gs-prod-bg-web.bio-iad.ea.com/render/?format=json&target=nonNegativeDerivative(sumSeriesWithWildcards(aliasByNode(eadp.gos.blaze.prod.nhl-2020-xone.*.logger.*.{ERR,FAIL})))"

    url = "http://gs-prod-bg-web.bio-iad.ea.com/render/?format=json&target=nonNegativeDerivative(sumSeriesWithWildcards(aliasByNode(eadp.gos.blaze.prod.nhl-2020-xone.*.logger.{system,slivers,user,redis}.{ERR,FAIL})))"

    #request = urllib3.PoolManager(retries=False)
    try:
        response = requests.get(url, timeout=Timeout)
        return response.json()
    except ValueError as e:
        plugin_exit(STATUS_UNK, "Can't connect to graphite URL: Please check service name", e)
    except Exception as e:
        plugin_exit(STATUS_UNK, "Can't connect to URL", e)

if len(sys.argv) < 2:
    if len(sys.argv) == 2:
        plugin_exit(STATUS_UNK, 'You must specify the timeout', '')


sc = SlackClient(TOKEN)
SERVICE = sys.argv[1]
TRESHOLD = sys.argv[2]
try:
    TIMEOUT = float(sys.argv[1])
except ValueError as e:
    plugin_exit(STATUS_UNK, "Argument for timeout must be float", e)
RESPONSE = fetch(TIMEOUT)
URLDATA = RESPONSE
ENDPOINTDATA = getendpoints(URLDATA)
print("----- ENDPOINTDATA -----")
print(ENDPOINTDATA)

if 'None' not in ENDPOINTDATA:
    if float(ENDPOINTDATA[0]) < float(TRESHOLD) and float(ENDPOINTDATA[1]) < float(TRESHOLD):
        plugin_exit(STATUS_OK, 'nhl-2020-xone Errors number below treshold', TRESHOLD)       
    elif float(ENDPOINTDATA[0]) > float(TRESHOLD) or float(ENDPOINTDATA[1]) > float(TRESHOLD):
        notifyissues(sc)
        plugin_exit(STATUS_CRIT, 'nhl-2020-xone Errors number is above treshold', TRESHOLD)
    elif all("None" in ENDPOINTDATA for x in ENDPOINTDATA): 
#        notifyFlatbehavior(sc)
        plugin_exit(STATUS_WARN, 'nhl-2020-xone data is flat with None Values', '')
