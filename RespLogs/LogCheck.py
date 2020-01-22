#!/usr/bin/python
import time
import re
import sys
from optparse import OptionParser

__author__ = 'Erick Ramirez <erickramirez@ea.com>'
__version__ = '0.06'

def findRange(loglines, type_, t1=None, t2=None):
    """Filter log lines with a certain message type and timeframe Message types
    can be, ERR,WARN,INFO,FATAL or ALL which is basically all of them."""
    newarray = []
    if t1 is not None and t2 is not None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct >= t1 and ct <= t2:
                    newarray.append(loglines[x])
            else:
                if ct >= t1 and ct <= t2 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])
    if t1 is not None and t2 is None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct >= t1:
                    newarray.append(loglines[x])
            else:
                if ct >= t1 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])
     
    if t1 is None and t2 is not None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                if ct <= t2:
                    newarray.append(loglines[x])
            else:
                if ct < t2 and type_ in loglines[x][1]:
                    newarray.append(loglines[x])
    if t1 is None and t2 is None:
        for x in range(len(loglines)):
            ct = time.strptime(loglines[x][0][:-7], '%Y/%m/%d-%H:%M')
            if type_ == 'ALL':
                newarray.append(loglines[x])
            else:
                if type_ in loglines[x][1]:
                    newarray.append(loglines[x])

    return newarray

def Report(log):
    """Create a report based on certain columns in the array
    and then filter by datetime (precision = minutes)."""
    logstrp = [[] for i in range(len(log))]
    for x in range(len(log)):
        logstrp[x].append(log[x][0][:-7])
        logstrp[x].append(log[x][1])
        logstrp[x].append(log[x][2])
        logstrp[x].append(log[x][3])
        neue = re.sub(r'0x[0-9a-f]+', '', log[x][5])
        logstrp[x].append(neue)
    uniqueList = []    
    for x in logstrp:
        if x not in uniqueList:
            uniqueList.append(x)
    for x in uniqueList:
        num = logstrp.count(x)
        print "%s" % num,
        print ' '.join(map(str, x))


def Total(log):
    """Create a report for all loglines discarding the time of the error."""
    logstrp = [[]for i in range(len(log))]
    for x in range(len(log)):
        logstrp[x].append(log[x][1])
        logstrp[x].append(log[x][2])
        logstrp[x].append(log[x][3])
        neue = re.sub(r'0x[0-9a-f]+', '', log[x][5])
        logstrp[x].append(neue)
    uniqueList = []
    for x in logstrp:
        if x not in uniqueList:
            uniqueList.append(x)
    for x in uniqueList:
        num = logstrp.count(x)
        print "%s" %num,
        print ' '.join(map(str, x))

def Unparsed(log):
    for x in log:
        print ' '.join(map(str, x))



def parse_options():
    parser = OptionParser(usage="usage: %prog -t ERR -b 2012/10/01-00:35 -f 2012/10/01-00:45 --total -F blaze_coreSlave1.log")
    parser.add_option('-b', '--begin', dest='begin', 
                      help='OPTIONAL: Begin Matching Time i.e: 2012/03/25-14:56')
    parser.add_option('-f', '--finish', dest='finish',
                      help='OPTIONAL: End Matching Time i.e: 2012/03/25-14:56')
    parser.add_option('-t', '--type', dest='type', default='ALL',
                      help='OPTIONAL: Filter by Message Type. i.e FATAL,ERR,WARN,INFO. Default is ALL')
    parser.add_option('--report', dest='report', action='store_true',
                      default=False, help='OPTIONAL: Creates a report filtered by minute')
    parser.add_option('--total', dest='total', action='store_true',
                      default=False, help='OPTIONAL: Prints total errors')
    parser.add_option('--unparsed', dest='unparsed', action='store_true',
                      default=False, help='OPTIONAL: Prints the filtered log with full values.')
    parser.add_option('-F', '--file', dest='file',
                      help='REQUIRED: Blaze log file name (i.e Blaze_Slavex.log or Blaze_coreSlavex.log')
    return parser.parse_args() # options, args


def validate_options(options):
    global begin, finish
    if options.file is None:
        sys.stderr.write("ERROR: Blaze log file missing.\n")
        sys.exit(1)
    if options.begin is not None:
        try:
            begin = time.strptime(options.begin, '%Y/%m/%d-%H:%M')
        except:
            print "ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00"
            sys.exit(1)
    else:
        begin = None

    if options.finish is not None:
        try:
            finish = time.strptime(options.finish, '%Y/%m/%d-%H:%M')
        except:
            print "ERROR: Date value incorrect. Correct syntax i.e 2012/12/30-05:00"
            sys.exit(1)
    else:
        finish = None
    if begin is not None and finish is not None:
        if begin >= finish:
            print "Begin time cannot be later or equal to Finish time"
            sys.exit(1)

def main():
    options, _ = parse_options()
    validate_options(options) # this could end in sys.exit!
    
    try:
        loglines = [logline.strip().split() for logline in open(options.file).readlines()] #Parse log file
    except IOError :
        print "ERROR: Could not open file."
        sys.exit(1)

    try:
        rangedvalues = findRange(loglines, options.type, begin, finish) #Get parsed data by range/type
    except ValueError:
        print "ERROR: Unsupported log format. Recommended logs blaze_slave<n>.log or blaze_coreSlave<n>.log"
        sys.exit(1)

    if options.report:
        sys.stderr.write('Report by minute:\n')
        Report(rangedvalues)

    if options.total:
        sys.stderr.write('Totals:\n')
        Total(rangedvalues)

    if options.unparsed:
        sys.stderr.write('Unparsed data:\n')
        Unparsed(rangedvalues)

if __name__ == '__main__':
    main()
