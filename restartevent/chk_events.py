import time
import os
import subprocess
import smtplib
from optparse import OptionParser
from email.mime.text import MIMEText

SLEEP_INTERVAL = 1.0
EVENTS = 14000
BASHCOMMAND = "/opt/gos-tools/EventAggregator/PROD/launchPROD.sh"

s = 0

def restart_process():
    for line in os.popen("ps aux | grep -n 'EventAggregator/PROD'|grep -v grep"):
        fields = line.split()
        pid = int(fields[1])
        os.kill(pid, 9)
        time.sleep(120)
        output = subprocess.Popen("cd ..; ./launchPROD.sh", stdout=subprocess.PIPE, shell=True)
        output.communicate()
        sal = "The Event Aggregator process has been restarted"
        msg = MIMEText(sal)
        msg["From"] = "InternalL2@alerts.ea.com"
        msg["To"] = "GS-L2Operations@ea.com,r1l4f7y6r7m6p4j4@electronic-arts.slack.com"
#        msg["To"] = "calarcon@contractor.ea.com"
        msg["Subject"] = "!!!!!!!! EVENT AGGREGATOR HAS BEEN RESTARTED  !!!!!!!!"
        p = subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
        time.sleep(120)

def readlines_then_tail(fin):
    "Iterate through lines and then tail for further lines."
    global s
    while True:
        line = fin.readline()
        if line:
            yield line
        else:
            s = 1
            tail(fin)

def tail(fin):
    "Listen for new lines added to file."
    print("Entro a funcion tail fin")
    while True:
        where = fin.tell()
        line = fin.readline()
        if not line:
            time.sleep(SLEEP_INTERVAL)
            fin.seek(where)
        else:
            yield line
            
def main():
    repeatevents = 0
    p = OptionParser("usage: chk_events.py file")
    (options, args) = p.parse_args()
    if len(args) < 1:
        p.error("must specify a file to watch")
    f = open(args[0], 'r')
    with f as fin:
        for line in readlines_then_tail(fin):
            parts = line.strip().split()
            if len(parts) > 1:
                events_values = parts[1]
                if parts[0] == "Received":
                    if int(parts[1]) < EVENTS:
                        if s == 0:
                            repeatevents = 0
                        repeatevents = repeatevents + 1
                        if (s == 1 and repeatevents > 4):
                            repeatevents = 0
                            restart_process()

if __name__ == '__main__':
    main()
