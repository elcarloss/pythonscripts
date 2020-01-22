#!/usr/bin/python2.7

import  argparse
import requests
from nagios import plugin_exit, STATUS_CRIT, STATUS_OK, STATUS_WARN, STATUS_UNK

GRAPHITE_URL = "http://{0}/render?format=json&target=alias\
(nonNegativeDerivative(scaleToSeconds(sumSeries(keepLastValue\
(exclude(prod.ccs.*.ccs-prod-ccs*.requests.postHosted_connections.\
{{{1},{1}{2}}}.*.{1}-20{2}-*.1-1.1.*.count,'CREATED')),keepLastValue\
(prod.ccs.*.ccs-prod-ccs*.requests.v1.postHosted_connections.\
{{{1},{1}{2}}}.*.{1}-20{2}-*.1-1.1.*.count)),60)),'Rate')\
&from=-5minutes"

GRAPHITE_URL_MEA = "http://{0}/render?format=json&target=\
alias(nonNegativeDerivative(scaleToSeconds(sumSeries(keepLastValue\
(exclude(prod.ccs.*.ccs-prod-ccs*.requests.postHosted_connections.\
{{{1},{1}{2}}}.*.{1}-20{2}-*.1-1.1.*.count,'CREATED')),\
keepLastValue(prod.ccs.*.ccs-prod-ccs*.requests.v1.\
postHosted_connections.mea.*.*.1-1.1.*.count)),60))\
,'Rate')&from=-5minutes"


def proc_datapoints(urldataf):
    """
    Give format to url data, get cssfailed of last 5 minutes
    """
    lstdatapoints = []
    try:
        if urldataf != None and "datapoints" in urldataf[0].keys():
            for datapoint in urldataf[0]["datapoints"]:
                if datapoint[0] is None:
                    lastdata = 0
                else:
                    lastdata = datapoint[0]
                lstdatapoints.append(lastdata)
            print("lstdatapoints: ",lstdatapoints)
            sumdatapoints = sum(lstdatapoints)
            return sumdatapoints
        else:
            plugin_exit(STATUS_UNK, "No data on URL", '')
    except IndexError as err:
        plugin_exit(STATUS_UNK, "Error in URL Data, check service and year", err)


def fetch_urldata(url, service, year, timeoutval):
    """
    Obtain the url data from the graphite url
    """
    if service == "mea":
        format_url = GRAPHITE_URL_MEA.format(url, service, year)
    else:
        format_url = GRAPHITE_URL.format(url, service, year)
    print(format_url)
    try:
        response = requests.get(format_url, timeout=timeoutval)
        return response.json()
    except ValueError as err:
        plugin_exit(STATUS_WARN, "Can't connect to graphite URL: Please check service name", err)
    except requests.exceptions.ReadTimeout as err:
        plugin_exit(STATUS_UNK, "Can't connect to URL", err)

def args_parser():
    """
    Parser for script arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--graphite', dest='graphite', metavar='STRING',
                        help='Graphite Host')
    parser.add_argument('-s', '--service', dest='service', metavar='STRING',
                        help='Service Name')
    parser.add_argument('-y', '--year', dest='year', metavar='STRING',
                        help='Year (YY)')
    parser.add_argument('-t', '--timeout', dest='timeout', metavar="DOUBLE",
                        default=4, help="Timeout for the alert")
    args = parser.parse_args()
    return args

def main():
    args = args_parser()
    if args.service == "mea":
        pass
    else:
        if not all([args.graphite, args.service, args.year]):
#        if args.graphite == None or args.service == None or args.year == None:
            plugin_exit(STATUS_UNK, 'You must specify graphite host, service name and year', '')

    service = args.service
    year = args.year
    graphurl = args.graphite

    try:
        timeout = float(args.timeout)
    except ValueError as err:
        plugin_exit(STATUS_UNK, "Argument for timeout must be float", err)
    urldata = fetch_urldata(graphurl, service, year, timeout)
    sumdatapoints = proc_datapoints(urldata)
    print(sumdatapoints)
    if sumdatapoints > 0:
        plugin_exit(STATUS_CRIT, 'Success Rate is 0', '')
    else:
        plugin_exit(STATUS_OK, 'Success Rate is ok', '')

if __name__ == '__main__':
    main()
