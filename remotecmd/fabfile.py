
from fabric.api import run

def anygs():
    #run("hostname; df -h; free -gt; ps aux|grep blazeserver|grep ufc")
    #run("hostname; sleep 1; ps -ef | grep 'dirtyCast.fifa-2018.ps4.prod' | grep 'portlist' --color=always")
    run("hostname;")
    #run("hostname")
#    run("ps -ef | egrep -i 'blaze|gos-ops|gos|voipserver|dirtycast|gameserver|cdc-ops|slave|mstr|slav|rdir|Feslconn|TheaterConn|Playnow|Ranking|qos|fesl|poller'")
