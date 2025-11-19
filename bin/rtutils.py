import rt.rest2
import configparser
import os
import sys


def get_rt():
    try:
        config = configparser.RawConfigParser()
        config.read(os.path.expanduser("~/.rtrcp"))
        rturl = "https://{0}".format(config.get("rt", "hostname"))
        rtpoint = "{0}/REST/2.0/".format(rturl)
        rt_token = config.get("rt", "token")
    except Exception as e:
        print(
            "Could not read config file or file is missing configuration elements:\n{}".format(
                e
            )
        )
        sys.exit(41)

    tracker = rt.rest2.Rt(rtpoint, token=rt_token)
    return tracker


def extract_custom_fields(ticket):
    for cf in ticket["CustomFields"]:
        if len(cf["values"]) > 0:
            ticket["CF.{" + cf["name"] + "}"] = (
                cf["values"] if len(cf["values"]) > 1 else cf["values"][0]
            )
        else:
            ticket["CF.{" + cf["name"] + "}"] = None
    return ticket
