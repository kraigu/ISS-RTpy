#!/usr/bin/env python

import rt.rest1
import sys
import argparse

from rtutils import get_rt, extract_custom_fields

aparse = argparse.ArgumentParser()
aparse.add_argument("ssubject")
args = aparse.parse_args()

tracker = get_rt()

try:
    # we're really only interested in incidents, this script might be named badly
    rquery = "Lifecycle = 'incidents' AND Subject LIKE '{}' AND Status != 'abandoned'".format(
        args.ssubject
    )
    tix = tracker.search(Queue=rt.rest1.ALL_QUEUES, raw_query=rquery)
except Exception as e:
    print(e)
    sys.exit(43)


for t in tix:
    t = extract_custom_fields(t)
    tid = t["id"].replace("ticket/", "")
    turl = "{}Ticket/Display.html?id={}".format(tracker.base_url, tid)
    tres = t["CF.{Resolution}"]
    if not tres:
        tres = "Still open"
    print(
        """ID: {0} ({4})
{3}
{1}
{2}
Resolution: {5}
Created: {6}\tUpdated: {7}
""".format(
            tid,
            t["Subject"],
            t["Queue"]["Name"],
            turl,
            t["Status"],
            tres,
            t["Created"],
            t["LastUpdated"],
        )
    )
