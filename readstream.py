# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

from tweepy import OAuthHandler, Stream, StreamListener

import configparser
import datetime
import time
import sys

config = configparser.ConfigParser()
config.read('settings.ini')

consumer_key = config['twitter']['consumer_key']
consumer_secret = config['twitter']['consumer_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

curdate = datetime.date.today().strftime("%Y%m%d")
filename = config['DEFAULT']['file']

file = open('{}_{}'.format(filename, curdate), 'a')

class ToFileListener(StreamListener):
    def on_data(self, data):
        file.write(data)
        return True

    def on_error(self, status):
        print('Error: {}'.format(status))
        if status == 420:
            return False

if __name__ == '__main__':
    l = ToFileListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    region = list(map(float, config['twitter']['region'].split(',')))

    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(locations = region, is_async=True)
        except:
            print('Unexpected error: ', sys.exc_info()[0])
            pass
        time.sleep(60)
