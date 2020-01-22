import os
import smtplib
import socket
import subprocess
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

hostname = socket.getfqdn()

def getPollerLogFiles():
    path = '/home/gos-ops/pollers/'
    file_list = []
    for root, dirs, files in os.walk(path, topdown=True):
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            if file.endswith("poller.log"):
        #        print(os.path.join(root, file))
                file_list.append(os.path.join(root, file))
    return file_list

def checkLogs(pollerFiles):
    print("=================================================================================================")
    data = {}
    for file in pollerFiles:
#        print("###############################################################################")
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        now = datetime.now()
#        print("Modification time: %s \nNow: %s" % (mtime.strftime('%H:%M:%S'), now.strftime('%H:%M:%S')))
        tdelta = datetime.strptime(str(now.strftime('%H:%M:%S')), '%H:%M:%S') - datetime.strptime(str(mtime.strftime('%H:%M:%S')), '%H:%M:%S')
        minutes, seconds = divmod(tdelta.seconds, 60)
#        print("File %s was las modified at %s, that was %s minutes and %s seconds ago" % (file, mtime, minutes, seconds))
#        print("---------------------------------------------------------------------------------")
        lines = subprocess.check_output(["tail", "-n5", file])
        if lines.count("Missed") >= 2:
            print("Found missing cycles!")
            print("Poller %s is having issues" % (file))
            # lines = process.output
#            print("Last 5 lines of log %s:" % (file))
#            print(lines)
#            print("=================================================================================================")
            data.update({file:lines})
        elif (minutes >= 900):
#            print("Mtime is greater than 900 minutes ago: %s" % (mtime))
            continue
        elif (minutes >= 10 and minutes <= 100):
#            print("Mtime is greater than 10 minutes ago: %s" % (mtime))
            continue
            data.update({file:lines})
        else:
            print("All good with poller %s" % (file))
    print("*************************************************************************************************************")
    print data
    if data:
        sendMail(data)

def sendMail(data):
    sender = "root@%s" % (hostname)
    receivers = ["GS-L2Operations@ea.com"]

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "There's a problem with a poller on %s!" % (hostname)
    msg['From'] = sender
    msg['To'] = ','.join(receivers)

    # Create the body of the message (a plain-text and an HTML version).
    text = "There were stuck pollers on %s: \n" % (hostname)
    text += "\n"
    texto =  subprocess.check_output("w | head -n 1 ", stderr=subprocess.STDOUT,  shell=True)
    text += "%s" % str(texto)
    text += "\n"
    texto =  subprocess.check_output("free -g ", stderr=subprocess.STDOUT,  shell=True)
    text += "%s" % str(texto)
    text += "\n"
    text += "================================================================================================\n\n"
    for poller in data:
        text += "Poller log: %s\n" % (poller)
        text += "Last 5 lines of log file: \n %s " % (data[poller])
    text += "================================================================================================\n\n"
    print (text)
    htmlBody = text.replace("\n", "<br />")
    htmlBody = htmlBody.replace("================================================================================================", "<hr />")
    html = """\
        <html>
            <head></head>
            <body>
                <p>
                    {0}
                </p>
            </body>
        </html>
    """.format(htmlBody)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(sender, receivers, msg.as_string())
    s.quit()

def main():
    pollerFiles = getPollerLogFiles()
    checkLogs(pollerFiles)

if __name__ == '__main__':
    main()

