import json
import urllib3
import xmltodict
import io
from deepdiff import DeepDiff


TITLESALERTS = {'nba-2016-ps4': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nba-2016-ps4',
                'nhl-2018-ps4-beta': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-ps4-beta',
                'nhl-2018-xone-beta': 'http://tools.internal.gosredirector.ea.com:42125/redirector/getServerList?name=nhl-2018-xone-beta'

                }


try:
    to_unicode = unicode
except NameError:
    to_unicode = str

with open('instances.json') as data_file:
    data_loaded = json.load(data_file)

con=0	
instancesdct = {}
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
    print(con)
    con += 1

if data_loaded==instancesdct:
    print("No changes in:",str(TITLESALERTS.keys()))
    print([len(v) for k,v in instancesdct.iteritems()])
else:
    print("Instance down")	
    with io.open('instances.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(instancesdct,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))


