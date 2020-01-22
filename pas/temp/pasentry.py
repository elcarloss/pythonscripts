#!/usr/bin/python2.7

"""
Add entrys to PAS
"""
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Date: June, 2017

import os
from optparse import OptionParser
from nagios import plugin_exit, STATUS_CRIT
from pas import PortService

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option('-e', '--environment', dest='enviro',
                      help='Environment prod, cert, dev, test')
    parser.add_option('-n', '--hostname', dest='hostname',
                      help='hostname to add entry to pas')
    parser.add_option('-i', '--internalip', dest='internalip',
                      help='Internal IP')
    parser.add_option('-x', '--externalip', dest='externalip',
                      help='External IP')


    (options, args) = parser.parse_args()

    os.system('clear')
    print'Processing....................................\n'

    env = options.enviro or None
    hostname = options.hostname or None
    internalip = options.internalip or None
    externalip = options.externalip or None


    if not all([env, hostname, internalip, externalip]):
        parser.print_help()
        plugin_exit(STATUS_CRIT,\
                  'Some parameter is missing, pasentry.py -e prod -n gossdevbeapp010.bio-sjc.ea.com -i 10.12.2.45 -x 159.54.12.5', "")
    portservice = PortService(env)
    if portservice.has_host(hostname):
        print"Hostname %s  is already added to pas in %s environment." %(hostname, env)
    else:
        try:
            portservice.add_host(hostname, internalip, externalip)
            print "                           *********** SUCCESS **************\n"
            print"Hostname %s in environment %s with internal ip %s and external ip %s is created correctly" %(hostname, env, internalip, externalip)
        except Exception as e:
            print "                                     ********** ERROR ************** \n"
        plugin_exit(STATUS_CRIT, 'Failed to add entry to pas  ---> ', e)
