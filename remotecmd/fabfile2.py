
from fabric.api import run

def anygs():
    run("hostname; df -h; free -gt")
#    run("ps -ef | egrep -i 'blaze|gos-ops|gos|voipserver|dirtycast|gameserver|cdc-ops|slave|mstr|slav|rdir|Feslconn|TheaterConn|Playnow|Ranking|qos|fesl|poller'")
