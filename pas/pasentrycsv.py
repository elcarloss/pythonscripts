#!/usr/bin/python2.7

"""
Import entries to PAS from an external file
"""
# Author: Carlos Alarcon
# GS-L2 Team
# Python version: 2.7
# Date: June, 2017

import os
import csv
from optparse import OptionParser
from nagios import plugin_exit, STATUS_CRIT
from pas import PortService

if __name__ == "__main__":
    PARSER = OptionParser()
    PARSER.add_option('-i', '--import', dest='impor',
                      help='Import a csv file')


    (options, args) = PARSER.parse_args()

    os.system('clear')
    print'Processing....................................'
    print'*********** Please erase all empty lines in the csv file before import *********\n'

    IMPCSV = options.impor or None

    if not all([IMPCSV]):
        PARSER.print_help()
        plugin_exit(STATUS_CRIT,\
                  'Some parameter is missing, pasentry.py -i file.csv', "")
    F = open(IMPCSV)
    CSV_F = csv.reader(F)
    for row in CSV_F:
        portservice = PortService(row[3])
        if portservice.has_host(row[0]):
            print"Hostname %s  is already added to pas in %s environment." %(row[0], row[3])
        else:
            try:
                portservice.add_host(row[0], row[1], row[2])
                print "                           *********** SUCCESS **************\n"
                print"Hostname %s in environment %s with internal ip %s and external ip %s is created correctly" \
	             %(row[0], row[3], row[1], row[2])
            except Exception as e:
                print "                                     ********** ERROR ************** \n"
                print"Failed to add entry to pas  ---> %s" %e
