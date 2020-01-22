#!/usr/local/bin/python2.7
import urllib2
import json
import subprocess
import shlex
import sys
import pdb
import cgi, cgitb
import csv


def getInfo(service,env):
    try:
        data = urllib2.urlopen('http://torch.gameservices.ea.com/metadata/titleData.json')
    except:
        data = urllib2.urlopen('http://gosprodbeapp0008.abn-sjc.ea.com/portal/titleData.json')

    salida = json.load(data)
    servicess = []
    listbz = []
    listdb = []
    listds = []
    listrd = []
    for product in salida:
        for blaze in product['serviceDescriptions']:
            if service == blaze['serviceName'] and env == blaze['environment']: 
                try:
                    listbz = [x for x in blaze['appHosts']]
                except:
                    pass

                try:
                    listdb = [x[:-5] for x in blaze['databaseInstances']]
                except:
                    pass

                try:
                    listds = [x[:-6] for x in blaze['servulatorInstances']]
                except:
                    pass

                try:
                    listrd = [x for x in blaze['redisClusters']['main']]
                except:
                    pass

    return sorted(listbz), sorted(listdb), sorted(listds), sorted(listrd), sorted(servicess)
    

# pdb.set_trace()

form = cgi.FieldStorage()
service = form.getvalue('service')
env = form.getvalue('env')
hostname = getInfo(service,env)


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
"""
print len(hostname[0]) 
print len(hostname[1]) 
print len(hostname[2])
"""
#print hostname[3]

ReDis = []
if hostname :
    print "<h1>%s" % (service)
    print """
     is built on:</h1>
	<table border="1" ><tr>
        <td>Host</td>
        <td>Technology</td>
	</tr>
    """ 
    for i in hostname[0]:
        print "<tr> <td>%s </td><td>Blaze</td> </tr>" % (i)
    for i in hostname[1]:
        print "<tr> <td>%s </td><td>Data Base</td> </tr>" % (i)
    if hostname[2]:
        for i in hostname[2]:
            print "<tr> <td>%s </td><td>DirtyCast</td> </tr>" % (i)
    if hostname[3]:
        for i in hostname[3]:
            print "<tr> <td>%s </td><td>Redis</td> </tr>" % (i)
    print "</table> Redis Chain: <br>"
# Generate redis chain
    if hostname[3]:
        for i in hostname[3]:
          ReDis.append(   env + "."  + service + ".main." + str(i).replace(".","_").replace(":",".") + "@" + str(i) )
print  ", ".join(ReDis)

print """
   	</div>
  	</section>
                <!-- Main -->
                        <div id="main" class="wrapper style1">
                                <div class="container">
                                        <!-- Content -->
                                                <section id="content">
     			<h1 >Hostname : </h1>
 					<form name="search" target="_self" action="apps/hostCheck/servicequery.py" method="get">
                                                <input type="text" name="host" size="100">
                                                <select name="env">
                                                <option value="prod" selected>Prod</option>
                                                <option value="cert">Cert</option>
                                                <option value="test">Test</option>
                                                <option value="dev">Dev</option>
                                                </select>
                                                <input type="submit" value="Submit">
                                                </form>
				</div>

                                                </section>

                                </div>
                        </div>


</body></html>
"""


