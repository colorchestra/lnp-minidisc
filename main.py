#!/usr/bin/env python
import feedparser
import time
import sys
import os
import logging
import requests
import subprocess
import re

os.chdir(os.path.dirname(os.path.realpath(__file__)))
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


url = "https://feeds.metaebene.me/lnp/m4a"
versionsOnly = False
timelimit = 1000
# TODO ask user
disc_length = 74

def formatOutput(article):
    output = color.BOLD + 'Aktuelle Episode:' + color.END + "\n     " + article['medium'] + " - " + article['title'] + "\n     " +  article['published'] + "\n     " + article['length'] + "\n     "
    article['description'] = article['description'].replace("\n", " ")  # replace newlines with spaces so descriptions don't look weird
    if not article['description'].startswith("<"):         # don't print html descriptions
            output = output + article['description'] + "\n"
    print(output)

def get_feed():
        global index, cachestring, article
        d = feedparser.parse(url)
        e = d.entries[0]

        # find correct links - could be improved with list comprehension
        for link in e['links']:
            if link['rel'] == 'enclosure':
                download_link = link['href']
                length = link['length']

        published_time = time.mktime(e.published_parsed)
        if int(time.time() - published_time) < int(timelimit * 60 * 60):
            # get episode number
            try:
                result = re.search(r"^LNP([0-9]{1,4}) *", e.title)
                episode_number = result.groups(1)
                print("episode_number: " + episode_number)
            except:
                print(f"{color.YELLOW}WARN Episode Number couldn't be verified{color.END}")
                episode_number = None
#            if e.title == re.match("^LNP[0-9]{1,4} *"):
#                print("Episode title is ")
            article = {'index': index, 'published': e.published, 'title': e.title, 'description': e.description, 'medium': d['feed']['title'], 'download_link': download_link, 'length': length, 'episode_number': episode_number}
            formatOutput(article)
                #cachestring = cachestring + e.link + "\n"
            index += 1


def download_episode():
    filename = article['download_link'].split('/')[-1]
    print("filename: " + filename)
    if not os.path.exists(filename):
        print("Downloading episode...")
        r = requests.get(article['download_link'])
        print(r.status_code)
        with open(filename,'wb') as output_file:
            output_file.write(r.content)
    return filename

def transfer_file():
    # TODO check what's on disc, wipe if necessary
    print(subprocess.run(f"netmd-cli send out_converted.wav", shell=True))

def cleanup():
    print("TODO - stub")



def convert_episode():

    print(subprocess.run(f"ffmpeg -y -i \"{episode_file}\" -f wav -ar 44100 -ac 2 out.wav", shell=True))  
    length_minutes = float(subprocess.run(f"soxi -D out.wav", shell=True, capture_output=True).stdout.decode()) * 60
    print(length_minutes)
    # dummy
    if length_minutes < disc_length: 
        print("File length is smaller than disc, using SP mode")
        copy_mode = "SP"
    elif length_minutes > disc_length < disc_length * 2:
        print("File length is bigger than disc, using LP2 mode")
        copy_mode = "LP2"
    elif length_minutes > disc_length * 2 < disc_length * 4:
        print("File length is bigger than disc, using LP4 mode")
        copy_mode = "LP4"
    else:
        print("File is too large to be copied. Exiting.")
        sys.exit(1)
    #print(subprocess.run(f"atracdenc -e atrac3 -i out.wav -o out.aea --bitrate 128", shell=True))  
    #print(subprocess.run(f"ffmpeg -i out.aea -f wav -c:a copy out.wav", shell=True))  

# TODO check for existence of dependencies

index = 0
get_feed()
episode_file = download_episode()
convert_episode()