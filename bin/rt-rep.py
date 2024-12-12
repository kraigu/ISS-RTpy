#!/usr/bin/env python3

import rt
import configparser
import os
import sys
import argparse
import datetime as DT
from dateutil.relativedelta import *

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

aparse = argparse.ArgumentParser(description="Report on RT incidents created during a given timespan (defaults to a summary of last month)")
aparse.add_argument("-s","--startdate", help="Start date of report")
aparse.add_argument("-e","--enddate", help="End date of report")
aparse.add_argument("-v","--verbose", action="store_true", help="Verbose report (print each ticket)")
args = aparse.parse_args()

tracker = rt.Rt(rtpoint, rtuser, rtpass)
try:
        tracker.login()
except Exception as e:
        print("Could not authenticate to RT:\n{}".format(e))
        sys.exit(42)

# if we need to calculate it on our own, then first day of last month
sdate = args.startdate or DT.date.today()+relativedelta(months=-1,day=1)
edate = args.enddate or DT.date.today()+relativedelta(day=1)
print("Searching between {} and {}".format(sdate,edate))

try:
	# raw search because we want to look at lifecycle, not supported in python-rt 1.0.9
	# ALL_QUEUES because LIKE functionality for queues not supported in python-rt 1.0.9
	rquery = "Lifecycle = 'incidents' AND Created > '{0}' AND Created < '{1}' AND Status != 'abandoned' AND CF.Resolution != 'abandoned' AND CF.Classification != 'Question Only'".format(sdate,edate)
	tix = tracker.search(Queue=rt.ALL_QUEUES, raw_query = rquery)
except Exception as e:
	print(e)
	sys.exit(43)

def print_summary():
	itypes = {}
	constits = {}
	severity = [0,0,0,0,0,0]
	for t in tix:
		itype = t['CF.{Classification}']
		constit = t['Queue'].replace('Incidents -','')
		itypes[itype] = itypes.get(itype, 0) + 1
		constits[constit] = constits.get(constit, 0) + 1
		# what a misbegotten use of try/except and I do it again later!
		try:
			severity[int(t['CF.{Risk Severity}'])] += 1
		except:
			severity[0] += 1
	for t in sorted(itypes):
		print("{}\t\t{}".format(itypes[t],t))
	print("\n")
	for i,s in enumerate(severity):
		print("Severity {}:\t{}".format(i,s))
	print("\n")
	for c in sorted(constits):
		print("{}\t\t{}".format(constits[c],c))


def print_verbose():
	for t in tix:
		tid = t['id'].replace('ticket/','')
		tconst = t['Queue'].replace('Incidents -','') or "Unset"
		try:
			tsev = int(t['CF.{Risk Severity}'])
		except:
			tsev = 0
		print("{}\t{}\t{}\t{}\t{}\t{}".format(tid,tconst,t['Created'],t['CF.{Classification}'],tsev,t['Subject']))

if args.verbose:
	print_verbose()
else:
	print_summary()
