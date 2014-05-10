import requests
import json
import time
import xml.etree.ElementTree as ET

lines = open("1000_rap_songs", "r").readlines()
lines = [x.strip() for x in lines]
lines = filter(lambda x: x and x[0] != '#', lines)
data = []
for line in lines:
    t = line.split(' - ')
    song = t[-1]
    artist = '-'.join(t[:-1])[5:]
    data.append((song, artist))
    
all_lyrics = json.load(open("lyrics", "r"))
all_songs = [x["song"] for x in all_lyrics]
for song, artist in data[818:]:
    if song in all_songs:
        continue
        
    time.sleep(20)
    try:
        r = requests.get("http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect", 
                    params = {"artist" : artist, 
                            "song" : song},
                    )
    except:
        print "Timed out getting {0} by {1}".format(song, artist)
        continue
    try:
        lyrics = ET.fromstring(r.text).find('{http://api.chartlyrics.com/}Lyric').text
    except:
        print "Couldn't get lyrics for {0} by {1}".format(song, artist)
        continue
    if not lyrics:
        print "Couldn't get lyrics for {0} by {1}".format(song, artist)
        continue
    all_lyrics.append({ "artist" : artist,
                        "song" : song,
                        "lyrics" : lyrics})
    all_songs.append(song)
    print "Got lyrics for {0} by {1}".format(song, artist)
    json.dump(all_lyrics, open("lyrics", "w"))
