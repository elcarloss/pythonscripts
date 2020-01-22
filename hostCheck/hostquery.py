#!/usr/local/bin/python2.7
import urllib2
import json
import subprocess
import shlex
import sys
import pdb
import cgi, cgitb
import csv
from HTMLParser import HTMLParser



def getInfo(hostname):
    try:
        data = urllib2.urlopen('http://torch.gameservices.ea.com/metadata/titleData.json')
    except:
        data = urllib2.urlopen('http://gosprodbeapp0008.abn-sjc.ea.com/portal/titleData.json')
        
    salida = json.load(data)
    listx = []
    for product in salida:
        for blaze in product['serviceDescriptions']:
            try:
                if hostname in blaze['appHosts']:
                    text = blaze['environment'].upper() + " " + blaze['serviceName'] + " Blaze"
                    listx.append(text)
                list2 = [x[:-6] for x in blaze['servulatorInstances']]
                dblist = [x[:-5] for x in blaze['databaseInstances']]
                if hostname in dblist:
                    text = blaze['environment'].upper() + " " + blaze['serviceName'] + " Database"
                    listx.append(text)
                if hostname in list2:
                    text = blaze['environment'].upper() + " " + blaze['serviceName'] + " Dirtycast"
                    listx.append(text)
            except:
                pass
    return listx
    


form = cgi.FieldStorage()
host = form.getvalue('host')
hostname = getInfo(host)


print "Content-type:text/html\r\n\r\n"
print """
<!DOCTYPE HTML>
<html>
        <head>
                <title>GOS - Host Check</title>
                <link rel="icon" type="image/png" href="/portal/images/favicon-32x32.png" sizes="32x32" />
                <link rel="icon" type="image/png" href="/portal/images/favicon-16x16.png" sizes="16x16" />

                <meta http-equiv="content-type" content="text/html; charset=utf-8" />
                <meta name="description" content="" />
                <meta name="keywords" content="" />
                <!--[if lte IE 8]><script src="/portal/css/ie/html5shiv.js"></script><![endif]-->
                <script src="/portal/js/jquery.min.js"></script>
                <script src="/portal/js/jquery.scrolly.min.js"></script>
                <script src="/portal/js/jquery.dropotron.min.js"></script>
                <script src="/portal/js/jquery.scrollex.min.js"></script>
                <script src="/portal/js/skel.min.js"></script>
                <script src="/portal/js/skel-layers.min.js"></script>
                <script src="/portal/js/init.js"></script>
                <noscript>
                        <link rel="stylesheet" href="/portal/css/skel.css" />
                        <link rel="stylesheet" href="/portal/css/style.css" />
                        <link rel="stylesheet" href="/portal/css/style-xlarge.css" />
                </noscript>
                <!--[if lte IE 9]><link rel="stylesheet" href="/portal/css/ie/v9.css" /><![endif]-->
                <!--[if lte IE 8]><link rel="stylesheet" href="/portal/css/ie/v8.css" /><![endif]-->
        </head>
        <body class="landing" >


                <!-- Header -->
                        <header id="header">
                                <h1 id="logo">GOS 24x7 - Host Check</h1>
                                <nav id="nav">
                                        <ul>
                                                <li><a href="/portal/index.html">Home</a></li>
                                                <li>
                                                        <a href="">Tools</a>
                                                        <ul>
                                                                <li><a href="/portal/portal.html">Host Check</a></li>
                                                                <li><a href="/portal/ipstrs.html">IPs and Traceroutes</a></li>
                                                                <li><a href="/portal/no=sidebar.html">No Sidebar</a></li>
                                                                </li>
                                                        </ul>
                                                </li>
                                        </ul>
                                </nav>
                        </header>

 <!-- Banner -->
                        <section id="banner">

			<div class="content">

"""
if hostname :
    print """
    <h1 > The hostname is listed on the below Blaze Environment:</h1>
	<table border="1" ><tr>
        <td>Enviroment</td>
        <td>Service Name</td>
        <td>Technology</td>
	</tr>
    """
    for i in hostname:
        h = i.split(" ")
        print "<tr><td> %s </td><td> %s </td><td> %s </td></tr>" % (h[0],h[1],h[2])
    print "</table>"

else :
    print """
     <h1 > The hostname is not presented on any blaze environment </br>
		but is listed on FLS Master File </h1>
     <table border="1" ><tr>
        <td>Hostname</td>
        <td>Master Title</td>
        </tr>
    """
    f = open('fls.csv','r').readlines()
    for line in f:
        try :
            if host in line:
                tmp = line.split()
                print "<tr><td> %s </td><td> %s </td></tr>" % (tmp[0], tmp[1])
        except:
            pass
    print " </table> "
print """
   	</div>
  	</section>
                <!-- Main -->
                        <div id="main" class="wrapper style1">
                                <div class="container">
                                        <!-- Content -->
                                                <section id="content">
     			<h1 >Hostname : </h1>
 					<form name="search" target="_self" action="/apps/hostCheck/hostquery.py" method="get">
                                                <input type="text" name="host" size="100">
                                                <input type="submit" value="Submit">
                                                </form>
				</div>

                                                </section>

                                </div>
                        </div>


"""
print "</body>"
print "</html>"


