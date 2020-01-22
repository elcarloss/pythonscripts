#!/usr/bin/env python

import json
import urllib2
import argparse
import socket
import string


def getHosts() :
   hostSet = set([])
   hostipExt = set([])
   titleData = urllib2.urlopen('http://torch.gameservices.ea.com/metadata/titleData.json')
   hostData = titleData.read()
   productData = json.loads(hostData)
   for product in productData:
       for title in product['serviceDescriptions']:
           if title['primary'] == True and title['technology'] == 'blaze' and title['serviceName']==OPTION.title and title['environment']==OPTION.env :
              for appHosts in title['appHosts']:
                 hostSet.add(appHosts)
              for appFrontEndsIps in title['appFrontEndIPs']:
                 hostipExt.add(appFrontEndsIps)
   print OPTION.title.upper()
   if hostSet != 0:
       for host in hostSet:
          address = socket.gethostbyname(host)
          print host, ' ', address
          print "\n"
       for hostextip in hostipExt:
          addressext = socket.gethostbyname(hostextip)
          print hostextip, ' ', addressext
          print "\n"
   else:
       print("There's no info about the title \n")


def main() :
   getHosts()

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Find IPs by title name using titleData')
    PARSER.add_argument("title", help="Title of the game")
    PARSER.add_argument("-e", "--env", default='prod', help="Environment, [prod|test]")
    OPTION = PARSER.parse_args()
    main()

