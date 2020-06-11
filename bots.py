# -*- coding: utf-8 -*-

import json
import re
import getopt
import sys
import os
import configparser

def checkbots(accounts):
    import botometer

    bots = []

    config = configparser.ConfigParser()
    config.read('settings.ini')

    rapidapi_key = config['rapidapi']['key']
    twitter_app_auth = {
        'consumer_key': config['twitter']['consumer_key'],
        'consumer_secret': config['twitter']['consumer_secret'],
        'access_token': config['twitter']['access_token'],
        'access_token_secret': config['twitter']['access_token_secret'],
    }

    bom = botometer.Botometer(wait_on_ratelimit = True,
                              rapidapi_key = rapidapi_key,
                              **twitter_app_auth)

    for screen_name, result in bom.check_accounts_in(accounts):
        if 'scores' in result:
            print("{} {}".format(screen_name.replace("@",""), result['scores']))
        else:
            print("{} not found".format(screen_name.replace("@","")))

def usage():
    print("options: ")
    print("\t-f | --file <filename>")

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:", ["file="])
        if len(opts) == 0:
            usage()
            sys.exit()
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)

    file = None

    for o, a in opts:
        if o in ("-f", "--file"):
            file = a
        else:
            assert False, "unhandled option"

    with open(file, 'r', encoding='utf-8') as file:
        users = file.readlines()
        checkbots(users)
