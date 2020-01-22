#!/usr/bin/python2.7
#
# Python Script to check status of dirtycast servers for Nagios 
#
# Note: this is a work in progress

import sys
import httplib
from optparse import OptionParser
import nagios

httplib.OK = 200	# This is standard define from python 2.5 on, but we're on 2.3

#
# Read and parse all command line option
#
parser = OptionParser()
parser.add_option("-H","--host",dest="host",help="Name or IP address of host to check")
parser.add_option("-p","--port",dest="port",help="Port to check on host")
parser.add_option("-m","--monitor",dest="monitor",default="/monitor",help="Default: \"/monitor\"")
parser.add_option("-s","--status",dest="status",default="/status",help="Default: \"/status\"")
(options, args) = parser.parse_args()
#
# This section opens an http connection, gets the 
# data from the status and monitor pages and closes connection
# in the event of error reading pages, it aborts.
#
try:
        conn = httplib.HTTPConnection(options.host,options.port)

        conn.request("GET", options.status)
        response = conn.getresponse()
        status2 = response.read()
        status = status2.splitlines()
except:
        nagios.plugin_exit(nagios.STATUS_UNK,'Unexpected error: '+str(sys.exc_info()),'')

if response.status != httplib.OK:
        if response.status == httplib.FOUND:
            nagios.plugin_exit(nagios.STATUS_UNK, 'Content blocked by EA Global Network Use and Security Policy' ,'')
        else:
            rstatus = str(response.status)+' '+response.reason+', Headers: '+str(response.getheaders())
            nagios.plugin_exit(nagios.STATUS_UNK, rstatus,'')
conn.close()

#
# Parse the status page information to extract relevant data.
#
serverload = systemload = clientsconnected = gameserversconnected = gamelatency = ''

# get the relevant lines
for line in status:
	if line.find('server load:') != -1:
		serverload = line
	elif line.find('system load average:') != -1:
		systemload = line
	elif line.find('clients connected:') != -1:
		clientsconnected = line
	elif line.find('gameservers connected:') != -1:
		gameserversconnected = line
	elif line.find('game latency:') != -1:
		gamelatency = line

# server load check
cpuload = 0
if serverload != '':
	cpuload = float(serverload.split()[2].split('=')[1])

# system load checks
# None for now

# clients connected check
clients = ['0', '0']
if clientsconnected != '':
	clients = clientsconnected.split()[2].split('/')

# gameservers connected checks
total = games = available = offline = stuck = 0
if gameserversconnected != '':
	total = int(gameserversconnected.split('/')[0].split()[2])
	gameserverbreakdown = gameserversconnected.split('(')[1][:-1].split(', ')
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
#
# Percent of Offline gameservers
#
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

#
# Now we interpret our results and set our return value accordingly
# NOTE: Since this is Nagios plugin we conform to Nagios return value std.
#
status = nagios.STATUS_OK
status_url = '<A href=http://' + options.host + ':' + options.port + options.status + '>Status Page</A>'
status_text = 'cpu:%3.2f clients:%s/%s games:%d/%d (%d offline)(%d stuck) %s' % (cpuload,clients[0],clients[1],games,total,offline,stuck,status_url)

if offline_percent > 20 :
	status = nagios.STATUS_CRIT
	status_text = '[OFFLINE] ' + status_text
elif offline_percent > 5 :
	status = nagios.STATUS_WARN
	status_text = '[OFFLINE] ' + status_text
elif gameserver_percent > 96 :
	status = nagios.STATUS_CRIT
	status_text = '[GAMES] ' + status_text
elif gameserver_percent > 90 :
	status = nagios.STATUS_WARN
	status_text = '[GAMES] ' + status_text
elif client_percent > 95:
	status = nagios.STATUS_CRIT
	status_text = '[CLIENTS] ' + status_text
elif client_percent > 90 :
	status = nagios.STATUS_WARN
	status_text = '[CLIENTS] ' + status_text
elif cpuload > 90 :
	status = nagios.STATUS_CRIT
	status_text = '[CPU] ' + status_text
elif stuck > 10:
	status = nagios.STATUS_CRIT
	status_text = '[STUCK] ' + status_text
elif stuck > 5:
	status = nagios.STATUS_WARN
	status_text = '[STUCK] ' + status_text
elif total == 0 :
        status = nagios.STATUS_WARN
        status_text = '[OFFLINE] ' + status_text

nagios.plugin_exit(status,status_text,'')

