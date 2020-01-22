import json
import getpass
import csv
import re
from pprint import pprint
from P4 import P4,P4Exception
from collections import defaultdict

#p4password = getpass.getpass(prompt='Enter your P4 password: ')
p4 = P4()
#p4.password = p4password

try:
	p4.connect()
	p4.run_login()
except P4Exception:
	for e in p4.errors:
		print e

final_report = {}
rid = 0
listafinal=[]
dic9=defaultdict(list)

with open('finalfile.txt', 'r') as in_file:
    for line in in_file:
	match = re.findall('^[//]+', line)
        if match:
	    listafinal.append(line)
	else:
	    listafinal.append(line)

for item in listafinal:
    if item[0:2] == '//':
	key = item
    else:
        dic9[key.rstrip()].append(item.rstrip())

datas = json.loads(json.dumps(dic9))

f = [f.strip() for f in open('endpoints.txt')]
x = 0
for jid,item in datas.iteritems():
	print "Service Name: " + item[0]
	print "Branch: " + jid
	for ep in f:
		cfg_result = p4.run("grep", "-i", "-n", "-l", "-s", "-e", ep, jid + "/.../*.cfg")
		boot_result = p4.run("grep", "-i", "-n", "-l", "-s", "-e", ep, jid + "/.../*.boot")
		if cfg_result:
			print "Found: " + ep + " in " + cfg_result[0]['depotFile']
			rid += 1
			final_report[rid] = {"ServiceName": item[0], "Branch": jid, "File": cfg_result[0]['depotFile'], "Endpoint": ep}
		if boot_result:
			print "Found: " + ep + " in " + boot_result[0]['depotFile']
			rid += 1
			final_report[rid] = {"ServiceName": item[0], "Branch": jid, "File": boot_result[0]['depotFile'], "Endpoint": ep}

report_writer = csv.DictWriter(open('nucleus_endpoints.csv', 'wb'), fieldnames=['Branch', 'Endpoint', 'File', 'ServiceName'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
report_writer.writeheader()
for fid,data in final_report.iteritems():
	pprint(data)
	report_writer.writerow(data)

p4.disconnect()
