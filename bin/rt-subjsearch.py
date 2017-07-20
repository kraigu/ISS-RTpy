#!/usr/bin/env python

import rt
import ConfigParser
import os
import sys
import argparse

try:
	config = ConfigParser.RawConfigParser()
	config.read(os.path.expanduser('~/.rtrcp'))
	rturl = "https://{0}".format(config.get('rt','hostname'))
	rtpoint = "{0}/REST/1.0/".format(rturl)
	rtuser = config.get('rt','username')
	rtpass = config.get('rt','password')
except Exception as e:
	print "Could not read config file or file is missing configuration elements:\n{}".format(e)
	sys.exit(41)

aparse = argparse.ArgumentParser()
aparse.add_argument("ssubject")
args = aparse.parse_args()

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print "Could not authenticate to RT:\n{}".format(e)
        sys.exit(42)

#tix = tracker.search(Queue='Incidents',raw_query="Subject LIKE '%Test%'")
try:
	# we're really only interested in incidents, this script might be named badly
	rquery = "Lifecycle = 'incidents' AND Subject LIKE '{}' AND Status != 'abandoned'".format(args.ssubject)
	tix = tracker.search(Queue=rt.ALL_QUEUES, raw_query = rquery)
except Exception as e:
	print e
	sys.exit(43)

for t in tix:
	tid = t['id'].replace('ticket/','')
	turl = "{}/Ticket/Display.html?id={}".format(rturl,tid)
	tres = t['CF.{Resolution}']
	if tres == '':
		tres = "Still open"
	tconst = t['Queue']
	if tconst == '':
		tconst = "Unset"
	print """{}:\t{}
{} / {}
{}
Status: {}\tResolution: {}
Created: {}\tUpdated: {}
""".format(tid,t['Subject'],t['Queue'],tconst,turl,t['Status'],tres,t['Created'],t['LastUpdated'])
