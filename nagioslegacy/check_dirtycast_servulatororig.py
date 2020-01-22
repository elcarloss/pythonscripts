#!/usr/bin/python2.7
'''
Python Script to check status of dirtycast servers for Nagios

Note: this is a work in progress
'''

from optparse import OptionParser
import requests
import nagios

#
# Read and parse all command line option
#
PARSER = OptionParser()
PARSER.add_option("-H", "--host", dest="host", help="Name or IP address of host to check")
PARSER.add_option("-i", "--id", dest="id", help="Voipserver id number")
PARSER.add_option("-t", "--title", dest="title", help="Title of monitor")
(OPTIONS, ARGS) = PARSER.parse_args()
#
# This section opens an http connection, gets the
# data from the status and monitor pages and closes connection
# in the event of error reading pages, it aborts.
#
try:
    URL = 'http://'+OPTIONS.host+':29000/proxy/'+OPTIONS.title+'/VS_Linux/0-'+OPTIONS.id+'/status'
    CONN = requests.get(URL)
    STATUS = CONN.text.splitlines()
except requests.exceptions.ConnectionError as err:
    nagios.plugin_exit(nagios.STATUS_UNK, "Can't connect to URL. "+err, '')

if CONN.status_code != 200:
    if CONN.status_code == 302:
        nagios.plugin_exit(nagios.STATUS_UNK, 'Content blocked by EA Global ' \
                           'Network Use and Security Policy', '')
    else:
        RSTATUS = str(CONN.status_code)
        nagios.plugin_exit(nagios.STATUS_UNK, RSTATUS, '')

#
# Parse the status page information to extract relevant data.
#
SERVERLOAD = SYSTEMLOAD = CLIENTSCONNECTED = GAMESERVERSCONNECTED = GAMELATENCY = ''

# get the relevant lines
for line in STATUS:
    if line.find('server load:') != -1:
        SERVERLOAD = line
    elif line.find('system load average:') != -1:
        SYSTEMLOAD = line
    elif line.find('clients connected:') != -1:
        CLIENTSCONNECTED = line
    elif line.find('gameservers connected:') != -1:
        GAMESERVERSCONNECTED = line
    elif line.find('game latency:') != -1:
        GAMELATENCY = line

# server load check
CPULOAD = 0
if SERVERLOAD != '':
    CPULOAD = float(SERVERLOAD.split()[2].split('=')[1])

# system load checks
# None for now

# clients connected check
CLIENTS = ['0', '0']
if CLIENTSCONNECTED != '':
    CLIENTS = CLIENTSCONNECTED.split()[2].split('/')

# gameservers connected checks
TOTAL = GAMES = AVAILABLE = OFFLINE = STUCK = 0
if GAMESERVERSCONNECTED != '':
    TOTAL = int(GAMESERVERSCONNECTED.split('/')[0].split()[2])
    GAMESERVERBREAKDOWN = GAMESERVERSCONNECTED.split('(')[1][:-1].split(', ')
    try:
        GAMES = int(GAMESERVERBREAKDOWN[0].split()[0])
    except IndexError:
        # we ignore values we don't find
        pass
    try:
        AVAILABLE = int(GAMESERVERBREAKDOWN[1].split()[0])
    except IndexError:
        # we ignore values we don't find
        pass
    try:
        OFFLINE = int(GAMESERVERBREAKDOWN[2].split()[0])
    except IndexError:
        # we ignore values we don't find
        pass
    try:
        STUCK = int(GAMESERVERBREAKDOWN[3].split()[0])
    except IndexError:
        # we ignore values we don't find
        pass
#
# Percent of Offline gameservers
#
if TOTAL > 0:
    OFFLINE_PERCENT = float(OFFLINE)/float(TOTAL) * 100
else:
    OFFLINE_PERCENT = 0

# game latency checks
# None for now
GAMESERVER_PERCENT = 0
if TOTAL != 0:
    GAMESERVER_PERCENT = GAMES * 100 / TOTAL

CLIENT_PERCENT = 0
if int(CLIENTS[1]) != 0:
    CLIENT_PERCENT = int(CLIENTS[0]) * 100 / int(CLIENTS[1])

#
# Now we interpret our results and set our return value accordingly
# NOTE: Since this is Nagios plugin we conform to Nagios return value std.
#
STATUS = nagios.STATUS_OK
STATUS_URL = '<A href=http://' + OPTIONS.host + ':29000/proxy/'+ \
             OPTIONS.title+'/VS_Linux/0-'+OPTIONS.id+'/status'
STATUS_TEXT = 'cpu:%3.2f clients:%s/%s games:%d/%d (%d offline)(%d stuck) %s' \
      % (CPULOAD, CLIENTS[0], CLIENTS[1], GAMES, TOTAL, OFFLINE, STUCK, STATUS_URL)

if OFFLINE_PERCENT > 20:
    STATUS = nagios.STATUS_CRIT
    STATUS_TEXT = '[OFFLINE] ' + STATUS_TEXT
elif OFFLINE_PERCENT > 5:
    STATUS = nagios.STATUS_WARN
    STATUS_TEXT = '[OFFLINE] ' + STATUS_TEXT
elif GAMESERVER_PERCENT > 96:
    STATUS = nagios.STATUS_CRIT
    STATUS_TEXT = '[GAMES] ' + STATUS_TEXT
elif GAMESERVER_PERCENT > 90:
    STATUS = nagios.STATUS_WARN
    STATUS_TEXT = '[GAMES] ' + STATUS_TEXT
elif CLIENT_PERCENT > 95:
    STATUS = nagios.STATUS_CRIT
    STATUS_TEXT = '[CLIENTS] ' + STATUS_TEXT
elif CLIENT_PERCENT > 90:
    STATUS = nagios.STATUS_WARN
    STATUS_TEXT = '[CLIENTS] ' + STATUS_TEXT
elif CPULOAD > 90:
    STATUS = nagios.STATUS_CRIT
    STATUS_TEXT = '[CPU] ' + STATUS_TEXT
elif STUCK > 10:
    STATUS = nagios.STATUS_CRIT
    STATUS_TEXT = '[STUCK] ' + STATUS_TEXT
elif STUCK > 5:
    STATUS = nagios.STATUS_WARN
    STATUS_TEXT = '[STUCK] ' + STATUS_TEXT
elif TOTAL == 0:
    STATUS = nagios.STATUS_WARN
    STATUS_TEXT = '[OFFLINE] ' + STATUS_TEXT

nagios.plugin_exit(STATUS, STATUS_TEXT, '')

