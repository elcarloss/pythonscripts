#!/bin/bash
#Activate python virtual environment
clear
echo "TO USE THIS SCRIPT YOU NEED TO ssh-agent bash and create a virtual python environment - source pyvirtual-bin-activate -"
echo "*************** OBTAIN THE LOGDIR PATH OF A GAME TITLE***************"
echo -e "Enter servicename to check (ex: nfs-2016-ps4): "
read servicename
echo -e "Enter environment: (prod/test/cert)"
read environment
logdir=$(python2.7 /home/calarcon/pyvirtual/scripts/remotecmd/remotecmd.py -c "ps -ef|grep logdir" -e $environment -s $servicename|awk '{print $26}'|grep log|uniq)
echo "The logdir path is: "$logdir


