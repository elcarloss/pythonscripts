
from fabric.api import run

def anygs():
#    run("ps -ef | egrep -i 'blaze|gos-ops|gos|voipserver|dirtycast|gameserver|cdc-ops|slave|mstr|slav|rdir|Feslconn|TheaterConn|Playnow|Ranking|qos|fesl|poller'")
    run("hostname")
    run("df -h")
    run("date")

