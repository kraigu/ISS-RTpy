#!/usr/bin/env python

import rt
import configparser
import os
import sys
import argparse

try:
	config = configparser.RawConfigParser()
	config.read(os.path.expanduser('~/.rtrcp'))
	rturl = "https://{0}".format(config.get('rt','hostname'))
	rtpoint = "{0}/REST/1.0/".format(rturl)
	rtuser = config.get('rt','username')
	rtpass = config.get('rt','password')
except Exception as e:
	print("Could not read config file or file is missing configuration elements:\n{}".format(e))
	sys.exit(41)

aparse = argparse.ArgumentParser()
aparse.add_argument("ssubject")
args = aparse.parse_args()

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print("Could not authenticate to RT:\n{}".format(e))
        sys.exit(42)

try:
	rquery = "Lifecycle = 'incidents' AND Status = '__Active__' AND CF.{{Userid}} = '{}'".format(args.ssubject)
	tix = tracker.search(Queue=rt.ALL_QUEUES, raw_query = rquery)
except Exception as e:
	print(e)
	sys.exit(43)

for t in tix:
	tid = t['id'].replace('ticket/','')
	turl = "{}/Ticket/Display.html?id={}".format(rturl,tid)
	tres = t['CF.{Resolution}']
	if tres == '':
		tres = "Still open"
	print("""ID: {0} ({4})
{3}
{1}
{2}
Resolution: {5}
Created: {6}\tUpdated: {7}
""".format(tid,t['Subject'],t['Queue'],turl,t['Status'],tres,t['Created'],t['LastUpdated']))

