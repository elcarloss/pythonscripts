#!/usr/bin/python2.7
'''
Python Script to check status of dirtycast servers for Nagios

'''

from optparse import OptionParser
import requests
import nagios

def main():
    #
    # Read and parse all command line option
    #

    parser = OptionParser()
    parser.add_option("-H", "--host", dest="host", help="Name or IP address" +
                      "of host to check")
    parser.add_option("-i", "--id", dest="id", help="Voipserver id number")
    parser.add_option("-t", "--title", dest="title", help="Title of monitor")
    (options, args) = parser.parse_args()

    #
    # This section opens an http connection, gets the
    # data from the status and monitor pages and closes connection
    # in the event of error reading pages, it aborts.
    #

    try:
        url = 'http://'+options.host+':29000/proxy/'+options.title+' \
              /VS_Linux/0-'+options.id+'/status'
        conn = requests.get(url)
        status = conn.text.splitlines()
    except requests.exceptions.RequestException as err:
        nagios.plugin_exit(nagios.STATUS_UNK, "Can't connect to url. "+err, '')

    if conn.status_code != 200:
        if conn.status_code == 302:
            nagios.plugin_exit(nagios.STATUS_UNK, 'Content blocked by EA Global ' \
                           'Network Use and Security Policy', '')
        else:
            rstatus = str(conn.status_code)
            nagios.plugin_exit(nagios.STATUS_UNK, rstatus, '')

    #
    # Parse the status page information to extract relevant data.
    #

    serverload = ''
    systemload = ''
    clientsconnected = ''
    gameserverconnected = ''
    gamelatency = ''

    # get the relevant lines

    for line in status:
        if line.find('server load:') != -1:
            serverload = line
        elif line.find('system load average:') != -1:
            systemload = line
        elif line.find('clients connected:') != -1:
            clientsconnected = line
        elif line.find('gameservers connected:') != -1:
            gameserverconnected = line
        elif line.find('game latency:') != -1:
            gamelatency = line

    # server load check
    cpuload = 0.0
    if serverload != '':
        cpuload = float(serverload.split()[2].split('=')[1])

    # system load checks
    # None for now

    # clients connected check

    clients = ['0', '0']
    if clientsconnected != '':
        clients = clientsconnected.split()[2].split('/')

    # gameservers connected checks

    total = 0
    games = 0
    available = 0
    offline = 0
    stuck = 0

    if gameserverconnected != '':
        total = int(gameserverconnected.split('/')[0].split()[2])
        gameserverbreakdown = gameserverconnected.split('(')[1][:-1].split(', ')
        try:
            games = int(gameserverbreakdown[0].split()[0])
        except IndexError:
        # we ignore values we don't find
            pass
        try:
            available = int(gameserverbreakdown[1].split()[0])
        except IndexError:
        # we ignore values we don't find
            pass
        try:
            offline = int(gameserverbreakdown[2].split()[0])
        except IndexError:
            # we ignore values we don't find
            pass
        try:
            stuck = int(gameserverbreakdown[3].split()[0])
        except IndexError:
        # we ignore values we don't find
            pass

    # Percent of offline gameservers


    if total > 0:
        offline_percent = float(offline)/float(total) * 100
    else:
        offline_percent = 0

    # game latency checks
    # None for now

    gameserver_percent = 0
    if total != 0:
        gameserver_percent = games * 100 / total

    client_percent = 0
    if int(clients[1]) != 0:
        client_percent = int(clients[0]) * 100 / int(clients[1])


    # Now we interpret our results and set our return value accordingly
    # NOTE: Since this is Nagios plugin we conform to Nagios return value std.

    status = nagios.STATUS_OK
    status_url = '<A href=http://' + options.host + ':29000/proxy/'+ \
                 options.title+'/VS_Linux/0-'+options.id+'/status'
    status_text = 'cpu:%3.2f clients:%s/%s games:%d/%d (%d offline)(%d stuck) %s' \
    % (cpuload, clients[0], clients[1], games, total, offline, stuck, status_url)

    if offline_percent > 20:
        status = nagios.STATUS_CRIT
        status_text = '[offline] ' + status_text
    elif offline_percent > 5:
        status = nagios.STATUS_WARN
        status_text = '[offline] ' + status_text
    elif gameserver_percent > 96:
        status = nagios.STATUS_CRIT
        status_text = '[games] ' + status_text
    elif gameserver_percent > 90:
        status = nagios.STATUS_WARN
        status_text = '[games] ' + status_text
    elif client_percent > 95:
        status = nagios.STATUS_CRIT
        status_text = '[clients] ' + status_text
    elif client_percent > 90:
        status = nagios.STATUS_WARN
        status_text = '[clients] ' + status_text
    elif cpuload > 90:
        status = nagios.STATUS_CRIT
        status_text = '[CPU] ' + status_text
    elif stuck > 10:
        status = nagios.STATUS_CRIT
        status_text = '[stuck] ' + status_text
    elif stuck > 5:
        status = nagios.STATUS_WARN
        status_text = '[stuck] ' + status_text
    elif total == 0:
        status = nagios.STATUS_WARN
        status_text = '[offline] ' + status_text

    nagios.plugin_exit(status, status_text, '')

if __name__ == '__main__':
    main()
