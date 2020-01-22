import json
import urllib3
import xmltodict
import io
import os
import smtplib
import socket
from yaml import load, dump
from deepdiff import DeepDiff
from datadiff import diff
from time import gmtime, strftime
from email.mime.multipart import MIMEMultipart
from email.mime.text import  MIMEText




TITLESALERTS = {
                'nba-2016-ps4': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-ps4',
                'nhl-2018-ps4-beta': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-ps4-beta',
		'nhl-2018-xone-beta': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-xone-beta',
                'masseffect-4-xone': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-xone',
                'masseffect-4-ps4': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-ps4',
                'masseffect-4-pc': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=masseffect-4-pc'
                }

def sendmail(dife):
    now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    me = "GS_L2Ops@ea.com"
    emails = "calarcon@contractor.ea.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "ALERT INSTANCES DOWN: "+now
    msg["From"] = me
    msg["You"] = emails
	

    text="Errors in instances"

    part1 = MIMEText(dife,"plain")

    msg.attach(part1)
	
    try:
    	s = smtplib.SMTP("localhost")
    	s.sendmail(msg["From"],emails,msg.as_string())
    	print "Email was sent"
    	s.quit()
    except:
	print "The message can't be sent"



#    os.system('echo "%s \n \n"| mail -s "Problem in instances", calarcon@contractor.ea.com .' %(dife))    

    
#    hostname = "gosrtbprapp0002.bio-sjc.ea.com" 
#    sender = "root@%s" % (hostname)
#    receivers = ["jacuna@contractor.ea.com", "calarcon@contractor.ea.com", "mbarbosa@contractor.ea.com", "ocalixto@contractor.ea.com", "ecastro@contractor.ea.com", "jgutierrez@contractor.ea.com", "jmendoza@contractor.ea.com", "eframirez@contractor.ea.com", "hrangel@contractor.ea.com", "ricrodriguez@contractor.ea.com"]
    
#    receivers = ["calarcon@contractor.ea.com"]
#    msg = MIMEText(str(dife))
#    msg['Subject'] = 'ALERT ABOUT INSTANCES AT ',now
#    msg['From'] = sender
#    msg['To'] = receivers
#    s = smtplib.SMTP('localhost')
#    s.sendmail(sender, receivers, msg.as_string())
#    s.quit()


try:
    to_unicode = unicode
except NameError:
    to_unicode = str

with open('instances.json') as data_file:
    data_loaded = load(data_file)

con=0	
instancesdct = {}
print("Processing .....")
for x in TITLESALERTS.values():
    lstinstances2=[]
    titledictv2={}
    http2v2 = urllib3.PoolManager(retries=False)
    titlexmlv2  = http2v2.request('GET', x, timeout=2)
    titledictv2= xmltodict.parse(titlexmlv2.data)
    titlejsonv2 = json.dumps(titledictv2)
    
    lstinstances2.append(str(titledictv2['serverlist']['servers']['serverinfodata']['masterinstance']['instancename']))

    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxmasters']['serverinstance']:
        lstinstances2.append(str(y.items()[4][1]))

    for y in titledictv2['serverlist']['servers']['serverinfodata']['instances']['serverinstance']:
        lstinstances2.append(str(y.items()[4][1]))
    for y in titledictv2['serverlist']['servers']['serverinfodata']['auxslaves']['serverinstance']:
        lstinstances2.append(str(y.items()[4][1]))

    instancesdct.update({TITLESALERTS.keys()[con]:lstinstances2})
#    print(x)   
    con += 1

	
difes =DeepDiff(instancesdct, data_loaded, ignore_order=True)
if difes.keys():
    print("Instance down")
    
    plan=str(difes)
    print(difes) 
    with io.open('instances.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(instancesdct,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))	
#    sendmail(plan)
else:
  print"No changes"
  print([len(v) for k,v in instancesdct.iteritems()])

