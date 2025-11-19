#!/usr/bin/env python3

import rt.rest1
import sys
import argparse
from rtutils import extract_custom_fields, get_rt

aparse = argparse.ArgumentParser()
aparse.add_argument("sip")
args = aparse.parse_args()

tracker = get_rt()

# tix = tracker.search(Queue='Incidents',raw_query="Subject LIKE '%Test%'")
try:
    qstring = """((Lifecycle = 'incidents' OR Lifecycle = 'investigations')) AND Status != 'abandoned' AND CF.{{IP}} = '{}'""".format(
        args.sip
    )
    print("DEBUG: {}".format(qstring))
    tix = list(tracker.search(Queue=rt.rest1.ALL_QUEUES, raw_query=qstring))
    # Need to stipulate ALL_QUEUES or it searches no queues
except Exception as e:
    print(e)
    sys.exit(43)

print("Found {} tickets".format(len(tix)))

for t in tix:
    t = extract_custom_fields(t)
    tid = t["id"].replace("ticket/", "")
    turl = "{}Ticket/Display.html?id={}".format(tracker.base_url, tid)
    if "CF.{Resolution}" in t:
        tres = t["CF.{Resolution}"]
    else:
        tres = "NA"

    if not tres:
        tres = "Still open"
    tconst = t["Queue"]["Name"]
    if tconst == "":
        tconst = "Unset"
    else:
        tconst = tconst.replace("Incidents - ", "")
        tconst = tconst.replace("Investigations - ", "")
    print(
        """{}:\t{}
{} / {}
{}
Status: {}\tResolution: {}
Created: {}\tUpdated: {}
""".format(
            tid,
            t["Subject"],
            t["Queue"]["Name"],
            tconst,
            turl,
            t["Status"],
            tres,
            t["Created"],
            t["LastUpdated"],
        )
    )
