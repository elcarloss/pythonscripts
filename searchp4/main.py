import json
import xml.etree.ElementTree as ET
from urllib2 import urlopen
from pprint import pprint

data = open("service_names.json", "r")
values = json.load(data)
data.close()
service_names = []
locations = {}
ind = 0
location_log = open("location_log.json", "wb+")

redirector_url = "http://internal.gosredirector.ea.com:42125/redirector/getServerList?name="

# print(type(values))
# pprint(len(values))

for idx in enumerate(values):
	value = idx[1]
	if (value['primary'] == True) and (value['environment'] == "prod"):
		# ind += 1
		service_names.append(value['serviceName'])
		# service_names[ind] = [value['serviceName'], value['environment']]

for service_name in service_names:
	url = redirector_url + service_name
	f = urlopen(url)
	tree = ET.parse(f)
	for elem in tree.iter('depotlocation'):
		print "Found info for: " + service_name
		print elem.text
		branch = elem.text.split(":")
		locations[service_name] = branch
		
json.dump(locations, location_log)
location_log.close()