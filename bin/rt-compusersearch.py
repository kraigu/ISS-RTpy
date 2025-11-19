#!/usr/bin/env python

import rt.rest1
import sys

from rtutils import extract_custom_fields, get_rt

tracker = get_rt()

try:
    rquery = "Lifecycle = 'incidents' AND Status = '__Active__' AND CF.{Classification} LIKE 'Compromised User Credentials'"
    tix = tracker.search(Queue=rt.rest1.ALL_QUEUES, raw_query=rquery)
except Exception as e:
    print(e)
    sys.exit(43)

for t in tix:
    t = extract_custom_fields(t)
    tid = t["id"].replace("ticket/", "")
    print("""{}\t{}\t{}""".format(tid, t["LastUpdated"], t["CF.{Userid}"]))
