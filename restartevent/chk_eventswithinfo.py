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
    veces = 0
    for line in os.popen("ps aux | grep -n 'EventAggregator/PROD'|grep -v grep"):
        print("Function to restart the EventAggregator Process")
        print("Entro ", veces , "veces")
        print("Function to restart the EventAggregator Process")
        print("Complete Line", line)
        fields = line.split()
        print("Line divided by fields :", fields)
        pid = int(fields[1])
        print("The EventsAggregator process is: ",pid)
	veces = veces + 1
        os.kill(pid, 9)
        print("EventAgreggator Process killed")
        time.sleep(10)
        output = subprocess.Popen("cd ..; ./launchPROD.sh", stdout=subprocess.PIPE, shell=True)
        output.communicate()
        print("EventAggregator Process Started")
        sal = "The Event Aggregator process has been restarted"
        msg = MIMEText(sal)
        print(sal)
        msg["From"] = "noreply@alerts.ea.com"
#    msg["To"] = "GS-L2Operations@ea.com,alarcon78@gmail.com"
#    msg["To"] = "GS-L2Operations@ea.com"
        msg["To"] = "calarcon@contractor.ea.com"
        msg["Subject"] = "!!!!!!!! EVENT AGGREGATOR HAS BEEN RESTARTED  !!!!!!!!"
        print("Mensaje a enviar por correo ")
        p = subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
        print('Before: %s' % time.ctime())
        time.sleep(240)
        print('After: %s\n' % time.ctime())

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
            print("No hay Linea Nueva")
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
        print(fin)
        for line in readlines_then_tail(fin):
            if repeatevents == 0:
                print("Repeat events = 0, entro o volvio a iniciar")
            parts = line.strip().split()
            if len(parts) > 1:
                events_values = parts[1]               
                if parts[0] == "Received":
                    if int(parts[1]) < EVENTS:
                        if s == 0:
                            repeatevents = 0
                        repeatevents = repeatevents + 1
                        print(parts)
                        print("s variable contents: ",s)
                        print("Repeat Event: ",repeatevents)
                        if (s == 1 and repeatevents > 4):
                            repeatevents = 0
                            restart_process()
#                            f.close()
                            print("Termino de reiniciar el proceso, cierro archivo y abro el archivo de nuevo")
#                            f = open(args[0], 'r')
if __name__ == '__main__':
    main()
