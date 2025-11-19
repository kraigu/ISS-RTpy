#!/usr/bin/env python3

import rt.rest1
import sys
import argparse
import datetime as DT
from dateutil.relativedelta import relativedelta

from rtutils import get_rt, extract_custom_fields


aparse = argparse.ArgumentParser(
    description="Report on RT incidents created during a given timespan (defaults to a summary of last month)"
)
aparse.add_argument("-s", "--startdate", help="Start date of report")
aparse.add_argument("-e", "--enddate", help="End date of report")
aparse.add_argument(
    "-v", "--verbose", action="store_true", help="Verbose report (print each ticket)"
)
args = aparse.parse_args()

tracker = get_rt()

# if we need to calculate it on our own, then first day of last month
sdate = args.startdate or DT.date.today() + relativedelta(months=-1, day=1)
edate = args.enddate or DT.date.today() + relativedelta(day=1)
print("Searching between {} and {}".format(sdate, edate))

try:
    # raw search because we want to look at lifecycle, not supported in python-rt 1.0.9
    # ALL_QUEUES because LIKE functionality for queues not supported in python-rt 1.0.9
    rquery = "Lifecycle = 'incidents' AND Created > '{0}' AND Created < '{1}' AND Status != 'abandoned' AND CF.Resolution != 'abandoned' AND CF.Classification != 'Question Only'".format(
        sdate, edate
    )
    tix = tracker.search(Queue=rt.rest1.ALL_QUEUES, raw_query=rquery)
except Exception as e:
    print(e)
    sys.exit(43)


def print_summary():
    itypes = {}
    constits = {}
    severity = [0, 0, 0]
    for t in tix:
        t = extract_custom_fields(t)
        itype = t["CF.{Classification}"] or "Unset"
        constit = t["Queue"]["Name"].replace("Incidents -", "").strip() or "Unset"
        itypes[itype] = itypes.get(itype, 0) + 1
        constits[constit] = constits.get(constit, 0) + 1
        # what a misbegotten use of try/except and I do it again later!
        try:
            severity[int(t["CF.{Incident Severity}"])] += 1
        except (ValueError, IndexError):
            severity[0] += 1
    for t in sorted(itypes):
        print("{}\t\t{}".format(itypes[t], t))
    print("\n")
    for i, s in enumerate(severity):
        print("Severity {}:\t{}".format(i, s))
    print("\n")
    for c in sorted(constits):
        print("{}\t\t{}".format(constits[c], c))


def print_verbose():
    for t in tix:
        t = extract_custom_fields(t)
        tid = t["id"].replace("ticket/", "")
        tconst = t["Queue"]["Name"].replace("Incidents -", "").strip()
        try:
            tsev = int(t["CF.{Incident Severity}"])
        except ValueError:
            tsev = 0
        print(
            "{}\t{}\t{}\t{}\t{}\t{}".format(
                tid, tconst, t["Created"], t["CF.{Classification}"], tsev, t["Subject"]
            )
        )


if args.verbose:
    print_verbose()
else:
    print_summary()
