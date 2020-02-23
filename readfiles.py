# -*- coding: utf-8 -*-

import json
import re
import getopt
import sys
import os

output = None

def readfile(name):
    global output

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
            
                strtweet = "|".join(map(str, [
                                 tweet['id'], 
                                 tweet['user']['screen_name'],
                                 tweet['user']['followers_count'], 
                                 tweet['user']['verified'],
                                 tweet['place']['name'],
                                 text,
                                 hashtags,
                                 mentions,
                                 " ".join(hashtags_text)
                                ]))
                if output:
                    output.write(strtweet + "\n")
                else:
                    print(strtweet)
            except:
                pass

def directory(path):
    for r, d, f in os.walk(path):
        for file in f:
            readfile(name = os.path.join(r, file))

def process(file, path):
    if file:
        readfile(name = file)
    elif path:
        directory(path = path)

def usage():
    print("readfiles.py\n\noptions: ")
    print("\t-h --help")
    print("\t-f | --file <filename>")
    print("\t-d | --directory <directory>")

def main():
    global output

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
    
    if outputname:
        output = open(outputname, 'w')

    process(file = file, path = directory)

    if output:
        output.close()

if __name__ == '__main__':
    main()