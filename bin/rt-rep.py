#!/usr/bin/env python

import rt
import ConfigParser
import os
import sys
import argparse
import datetime as DT
from dateutil.relativedelta import *

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

aparse = argparse.ArgumentParser(description="Report on RT incidents created during a given timespan (defaults to a summary of last month)")
aparse.add_argument("-s","--startdate", help="Start date of report")
aparse.add_argument("-e","--enddate", help="End date of report")
aparse.add_argument("-v","--verbose", action="store_true", help="Verbose report (print each ticket)")
args = aparse.parse_args()

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print "Could not authenticate to RT:\n{}".format(e)
        sys.exit(42)

if args.startdate is not None:
	sdate = args.startdate
else:
	# need to calculate it on our own
	# first day of last month
	sdate = DT.date.today()+relativedelta(months=-1,day=1)

if args.enddate is not None:
	edate = args.enddate
else:
	edate = DT.date.today()+relativedelta(day=1)

print "Searching between {} and {}".format(sdate,edate)

try:
	tix = tracker.search(Queue='Incidents', order='Created', Created__gt = sdate, Created__lt = edate)
except Exception as e:
	print e
	sys.exit(43)

def print_summary():
	itypes = {}
	constits = {}

	for t in tix:
		itype = t['CF.{Classification}']
		constit = t['CF.{Constituency}']
		if itype in itypes:
			itypes[itype] += 1
		else:
			itypes[itype] = 1
		if constit in constits:
			constits[constit] += 1
		else:
			constits[constit] = 1

	for t in sorted(itypes):
		print "{}\t\t{}".format(itypes[t],t)
	print "\n"
	for c in sorted(constits):
		print "{}\t\t{}".format(constits[c],c)

def print_verbose():
	for t in tix:
		tid = t['id'].replace('ticket/','')
		tconst = t['CF.{Constituency}']
		if tconst == '':
			tconst = "Unset"
		print "{}\t{}\t{}".format(tid,tconst,t['Subject'])

if args.verbose:
	print_verbose()
else:
	print_summary()
