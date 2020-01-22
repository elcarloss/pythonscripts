#!/bin/bash

echo -e '====================================================================================================================\n'
echo -e 'Hostname: '
hostname
echo -e '\nIP Address:'
/sbin/ifconfig | grep 'inet addr' | awk '{print $2}' | cut -d':' -f2
echo -e '\nMemory (in MB):'
free -m
echo -e '\nCPU Utilization:'
mpstat -P ALL
echo -e '\nDisk utilization:'
df -hT
echo -e '\nTop 5 processes (by memory usage):'
ps -eo pmem,pcpu,vsize,pid,cmd | sort -k 1 -nr | head -5
echo -e '\n'

