# -*- coding: utf-8 -*-

import json
import re
import getopt
import sys
import os
import configparser

from collections import OrderedDict

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

    bom = botometer.Botometer(wait_on_ratelimit=True,
                              rapidapi_key=rapidapi_key,
                              **twitter_app_auth)

    for screen_name, result in bom.check_accounts_in(accounts):
        # 0.6
        # https://blog.quantinsti.com/detecting-bots-twitter-botometer/
        # all() or any()
        if 'scores' in result:
            if any(i >= 0.6 for i in list(result['scores'].values())):
                print("{} {}".format(screen_name, result['scores']))
                bots.append(screen_name.replace("@",""))

    return bots

def readfile(name):
    def group(num):
        if num < 10000:
            return 1 # Usuario, menos de 10k falloweres
        elif num < 100000:
            return 2 # Micro influencer, menos de 100k fallowers
        elif num < 700000:
            return 3 # Influencer, menos de 700k fallowers
        else:
            return 4 # Celebrity

    def device(source):
        if ('iPhone' in source) or ('iOS' in source) or ('iPad' in source) or ('Mac' in source):
            return 'Apple'
        elif 'Android' in source:
            return 'Android'
        elif ('Mobile' in source) or ('App' in source):
            return 'Mobile device'
        elif 'Windows' in source:
            return 'Windows'
        elif 'Bot' in source:
            return 'Bot'
        elif 'Web' in source:
            return 'Web'
        elif 'Instagram' in source:
            return 'Instagram'
        elif 'TweetDeck' in source:
            return 'TweetDeck'
        else:
            return 'Unknown'

    result = []
    regex_http = re.compile("(http|https)\:\/\/.*(\s|$)", re.UNICODE)
    regex_user = re.compile("@\w+", re.UNICODE)
    regex_hash = re.compile("#\w+")
    
    with open(name, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                tweet = json.loads(line)
                
                text = tweet['extended_tweet']['full_text'] if 'extended_tweet' in tweet else tweet['text']
                text = text.replace("\n"," ")
                text = regex_http.sub("", text)
                text = regex_user.sub("", text)

                hashtags_text = regex_hash.findall(text)

                hashtags = " ".join([ t['text'] for t in tweet['entities']['hashtags'] ]) if len(tweet['entities']['hashtags']) > 0 else ""
                mentions = " ".join([ t['screen_name'] for t in tweet['entities']['user_mentions'] ]) if len(tweet['entities']['user_mentions']) > 0 else "" 
            
                t = OrderedDict()
                t['id'] = tweet['id']
                t['file'] = name.split("/")[-1]
                t['user'] = tweet['user']['screen_name']
                t['device'] = device(tweet['source'])
                t['followers'] = tweet['user']['followers_count']
                t['group'] = group(int(tweet['user']['followers_count']))
                t['origin'] = tweet['place']['name'] if tweet['place']['place_type'] == 'city' else tweet['place']['country']
                t['text'] = text
                t['hashtags'] = hashtags
                t['mentions'] = mentions
                t['hashtags_text'] = " ".join(hashtags_text)

                result.append(t)
            except:
                pass

    return result

def directory(path):
    result = []
    for r, d, f in os.walk(path):
        for file in f:
            result = result + readfile(name = os.path.join(r, file))
    return result

def process(file, path):
    if file:
        return readfile(name = file)
    elif path:
        return directory(path = path)

def usage():
    print("readfiles.py\n\noptions: ")
    print("\t-h --help")
    print("\t-f | --file <filename>")
    print("\t-d | --directory <directory>")
    print("\t-o | --output <filename>")

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:d:o:", ["help", "file=", "directory=", "output="])
        if len(opts) == 0:
            usage()
            sys.exit()
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)

    file = None
    directory = None
    outputname = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--file"):
            file = a
        elif o in ("-d", "--directory"):
            directory = a
        elif o in ("-o", "--output"):
            outputname = a
        else:
            assert False, "unhandled option"
    
    # Process
    result = process(file = file, path = directory)

    # Users
    users = [ "@{}".format(tweet['user']) for tweet in result]
    users_set = set(users)
    users = list(users_set)

    # Check Bot
    bots = checkbots(users)
    for t in range(0, len(result)):
        if result[t]['user'] in bots:
            result[t]['group'] = '5'

    print("tweets: ", len(result))
    print("users: ", len(users))
    print("bots: ", len(bots))

    # Output
    if not outputname:
        for tweet in result:
            print("|".join(str(v) for v in tweet.values()))
    else:
        file = open(outputname, 'w')
        for tweet in result:
            file.write("|".join(str(v) for v in tweet.values()) + "\n")
        file.close()

if __name__ == '__main__':
    main()