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
aparse.add_argument("sip")
args = aparse.parse_args()

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print "Could not authenticate to RT:\n{}".format(e)
        sys.exit(42)

#tix = tracker.search(Queue='Incidents',raw_query="Subject LIKE '%Test%'")
try:
	qstring = """((Lifecycle = 'incidents' OR Lifecycle = 'investigations')) AND Status != 'abandoned' AND CF.{{IP}} = '{}'""".format(args.sip)
	print "DEBUG: {}".format(qstring)
	tix = tracker.search(Queue=rt.ALL_QUEUES,raw_query=qstring)
	# Need to stipulate ALL_QUEUES or it searches no queues
except Exception as e:
	print e
	sys.exit(43)

print "Found {} tickets".format(len(tix))

for t in tix:
	tid = t['id'].replace('ticket/','')
	turl = "{}/Ticket/Display.html?id={}".format(rturl,tid)
	if 'CF.{Resolution' in t:
		tres = t['CF.{Resolution}']
	else:
		tres = 'NA'

	if tres == '':
		tres = "Still open"
	tconst = t['Queue']
	if tconst == '':
		tconst = "Unset"
	else:
		tconst = tconst.replace('Incidents - ','')
		tconst = tconst.replace('Investigations - ','')
	print """{}:\t{}
{} / {}
{}
Status: {}\tResolution: {}
Created: {}\tUpdated: {}
""".format(tid,t['Subject'],t['Queue'],tconst,turl,t['Status'],tres,t['Created'],t['LastUpdated'])
