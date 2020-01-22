import json
import getpass
import csv
from pprint import pprint
from P4 import P4,P4Exception

p4password = getpass.getpass(prompt='Enter your P4 password: ')
p4 = P4()
p4.password = p4password
lista=[]
list2=[]
try:
	p4.connect()
	p4.run_login()
except P4Exception:
	for e in p4.errors:
		print e

file = open("branchesjul2017.txt", "r")
for linea in file.readlines():
    lista.append(linea)
file.close()
for line in range(len(lista)):
    list2.append(lista[line].rstrip())
final_report = {}
rid = 0

f = [f.strip() for f in open('endpoints.txt')]
for item in range(len(list2)):
	for ep in f:
		cfg_result = p4.run("grep", "-i", "-n", "-l", "-s", "-e", ep, list2[item] + "/.../*.cfg")
		boot_result = p4.run("grep", "-i", "-n", "-l", "-s", "-e", ep, list2[item] + "/.../*.boot")
		if cfg_result:
			print "Found: " + ep + " in " + cfg_result[0]['depotFile']
			rid += 1
			final_report[rid] = {"Branch": list2[item], "File": cfg_result[0]['depotFile'], "Endpoint": ep}
		if boot_result:
			print "Found: " + ep + " in " + boot_result[0]['depotFile']
			rid += 1
			final_report[rid] = {"Branch": list2[item], "File": boot_result[0]['depotFile'], "Endpoint": ep}

report_writer = csv.DictWriter(open('nucendpoints.csv', 'wb'), fieldnames=['Branch', 'Endpoint', 'File'], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
report_writer.writeheader()
for fid,data in final_report.iteritems():
	pprint(data)
	report_writer.writerow(data)
p4.disconnect()



