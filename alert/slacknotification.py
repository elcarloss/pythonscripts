#!/usr/bin/env python

import requests
import json
import argparse
import time

def upnotification(servicename, instance):
    alerttitle = ' '.join(servicename.upper().split('-'))
    url = 'https://hooks.slack.com/services/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'
    headers = {'Content-type': 'application/json'}
    data = {"attachments": [   
           {
            "fallback": "Instance up",
            "color": "good",
            "pretext": "Blaze instance changed to *UP* :heavy_check_mark:",
            "author_name": "GS Blaze",
            "title": alerttitle,
            "title_link": "https://goscc.online.ea.com/servers/detail/PROD/{0}".format(servicename),
            "fields": [
                {
                    "title": "Instances",
                    "value": instance,
                },
            ],
            "footer": "GS",
            "ts": time.time()
        }
    ]
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)

def downnotification(servicename, instance):
    alerttitle = ' '.join(servicename.upper().split('-'))
    url = 'https://hooks.slack.com/services/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'
    headers = {'Content-type': 'application/json'}
    data = {"attachments": [   
           {
            "fallback": "Instance down",
            "color": "danger",
            "pretext": "Blaze instance changed to*DOWN* :x:",
            "author_name": "GS Blaze",
            "title": alerttitle,
            "title_link": "https://goscc.online.ea.com/servers/detail/PROD/{0}".format(servicename),
            "fields": [
                {
                    "title": "Instances",
                    "value": instance,
                },
            ],
            "footer": "GS",
            "ts": time.time()
        }
    ]
    }
    r = requests.post(url, data=json.dumps(data), headers=headers)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Send slack notification')
    PARSER.add_argument("servicename", help="title of the game")
    PARSER.add_argument("branch", help="Branch of the game")
    OPTION = PARSER.parse_args()
    upnotification(OPTION.servicename, OPTION.branch)
    downnotification(OPTION.servicename, OPTION.branch)
