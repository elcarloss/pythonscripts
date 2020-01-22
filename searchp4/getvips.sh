#!/bin/bash 
today=$(date +%Y%m%d)
echo $today
echo "Downloading and processing serverlist from internal.gosredirector.ea.com ......."
curl http://internal.gosredirector.ea.com:42125/redirector/getServerList?name= > /home/calarcon/pyvirtual/scripts/searchp4/depo3.txt
cat /home/calarcon/pyvirtual/scripts/searchp4/depo3.txt |egrep 'depotlocation|servicename' > /home/calarcon/pyvirtual/scripts/searchp4/depotsname1.txt
grep -vwE "(<servicenames>|</servicenames>)" /home/calarcon/pyvirtual/scripts/searchp4/depotsname1.txt |cut -b 31-|cut -d '<' -f 1|cut -d ":" -f 3 > /home/calarcon/pyvirtual/scripts/searchp4/finalfile.txt

python2.7 /home/calarcon/pyvirtual/scripts/searchp4/genhzcsv.py
