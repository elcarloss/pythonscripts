#!/usr/bin/env python

import os
import sys


class Validateinservice:  
    def __init__(self, xmlredir, instanceargument):
        self.xmlredir = xmlredir
        self.instanceargument =  instanceargument
        instanceargumentmaster = "temp"
        lenstance = len(self.instanceargument)
        indexkeywords = instanceargument.rfind("Slave")
        indexkeywordm = instanceargument.rfind("Master")


    def auxmasters (self):
        lenmasterinstancesredirector = len(self.xmlredir['serverlist']['servers']['serverinfodata']
                                                   ['auxmasters']['serverinstance'])
        for x in range(lenmasterinstancesredirector):
            if self.instanceargument in (self.xmlredir['serverlist']['servers']['serverinfodata']
                                            ['auxmasters']['serverinstance'][x]['instancename']):
               if (self.xmlredir['serverlist']['servers']['serverinfodata']['auxmasters']
                           ['serverinstance'][x]['inservice']) == "0":
                   return(0)
        return(1)
   
    def __str__(self):
        return "%s" % (self.auxmasters)

#    def auxslaves (self):
#        lenauxslaveinstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']
#                                                     ['auxslaves']['serverinstance'])
#        for x in range(lenauxslaveinstancesredirector):
#            if instanceargument in (xmlredir['serverlist']['servers']['serverinfodata']
#                                            ['auxslaves']['serverinstance'][x]['instancename']):
#               if (xmlredir['serverlist']['servers']['serverinfodata']['auxslaves']
#                           ['serverinstance'][x]['inservice']) == "0":
#                   print("Instancia Encontrada con 0 en servicio")
#                   return(self, 0)
#        return(self, 1)

 #   def coreslaves (self):
 #       lenslaveinstancesredirector = len(xmlredir['serverlist']['servers']['serverinfodata']
 #                                                 ['instances']['serverinstance'])
 #       for x in range(lenslaveinstancesredirector):
 #           if instanceargument in (xmlredir['serverlist']['servers']['serverinfodata']
 #                                           ['instances']['serverinstance'][x]['instancename']):
 #               if (xmlredir['serverlist']['servers']['serverinfodata']['instances']
 #                           ['serverinstance'][x]['inservice']) == "0":
 #                   return(self, 0)
 #           return(self, 1)
  #      else:
  #          return(self, 1)
