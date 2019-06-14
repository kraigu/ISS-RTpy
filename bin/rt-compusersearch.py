#!/usr/bin/env python

import rt
import configparser
import os
import sys

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

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print("Could not authenticate to RT:\n{}".format(e))
        sys.exit(42)

try:
	rquery = "Lifecycle = 'incidents' AND Status = '__Active__' AND CF.{Classification} LIKE 'Compromised User Credentials'"
	tix = tracker.search(Queue=rt.ALL_QUEUES, raw_query = rquery)
except Exception as e:
	print(e)
	sys.exit(43)

for t in tix:
	tid = t['id'].replace('ticket/','')
	print("""{}\t{}\t{}""".format(tid,t['LastUpdated'],t['CF.{Userid}']))
