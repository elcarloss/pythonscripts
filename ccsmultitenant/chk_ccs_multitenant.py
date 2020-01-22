#!/usr/bin/python2.7

"""
Monitoring alert to verify if the ccs value from multitenant graphite is minor than treshold.
"""

import sys
import requests
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK
from slackclient import SlackClient



TOKEN = "xoxp-3339495132-113342057840-750781819203-bfdb0a703a44ac686e6d18b03bfd0c09"
TRESHOLD = '10.0'
CHANNEL = "gs-blaze-alerts"

def notifyissues(sc):
    msg_issues = "!!ALERT!! CCS rate is greater than treshold !!ALERT!!"
    sc.api_call('chat.postMessage', channel=CHANNEL, text=msg_issues, username='ccs_alert', icon_emoji=':siren:')

def notifyNOissues(sc):
    msg_issues = "All is fine"
    sc.api_call('chat.postMessage', channel=CHANNEL, text=msg_issues, username='ccs_alert', icon_emoji=':siren:')

def notifyFlatbehavior(sc):
    msg_issues = "!!WARNING!! CCS rate is flat with None values !!WARNING!!"
    sc.api_call('chat.postMessage', channel="gs-opsmx-internal", text=msg_issues, username='ccs_alert', icon_emoji=':siren:')

def getendpoints(urldataf):
    """
    Give format to url data
    """
    if urldataf != None and "datapoints" in urldataf[0].keys():
        try:
            lstendpoints = []
            leng = len(urldataf[0]["datapoints"])
#            print(str(urldataf[0]["datapoints"][leng-1][0]).translate(None,"'"))
#            print(str(urldataf[0]["datapoints"][leng-2][0]).translate(None,"'"))
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

#    url = "http://internal.graphite.renderer.gos.gameservices.ea.com/render/?format=json&target=nonNegativeDerivative(scaleToSeconds(sumSeries(keepLastValue(prod.ccs.*.ccs-prod-ccs*.requests.v*.postHosted_connections.{global,openduration}.*.*.1-1.*.*.count)),60))"
    url ="http://internal.graphite.renderer.gos.gameservices.ea.com/render/?format=json&target=nonNegativeDerivative(scaleToSeconds(sumSeries(keepLastValue(prod.ccs.*.ccs-prod-ccs*.requests.v*.postHosted_connections.{global,openduration}.*.*.1-1.*.*.count)),60)),%27DC_INSTANCE_ERROR%27)"

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
try:
    TIMEOUT = float(sys.argv[1])
except ValueError as e:
    plugin_exit(STATUS_UNK, "Argument for timeout must be float", e)
RESPONSE = fetch(TIMEOUT)
URLDATA = RESPONSE
ENDPOINTDATA = getendpoints(URLDATA)
print("----- ENDPOINTDATA -----")
print(ENDPOINTDATA)

if 'null' not in ENDPOINTDATA:
    if float(ENDPOINTDATA[0]) < float(TRESHOLD) and float(ENDPOINTDATA[1]) < float(TRESHOLD):
        plugin_exit(STATUS_OK, 'CCS rate is ok', '')       
    elif float(ENDPOINTDATA[0]) > float(TRESHOLD) or float(ENDPOINTDATA[1]) > float(TRESHOLD):
        notifyissues(sc)
        plugin_exit(STATUS_CRIT, 'CCS rate is greater than treshold', '')
    elif all("None" in ENDPOINTDATA for x in ENDPOINTDATA): 
        #notifyFlatbehavior(sc)
        plugin_exit(STATUS_WARN, 'CCS Rate is flat with None Values', '')
