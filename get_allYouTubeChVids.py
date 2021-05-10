# -*- coding: utf-8 -*-
"""get_All_Videos.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14A4xU1vKkyKhpA2mOqILYSZta87que7O
"""

# import libraries 
from apiclient.discovery import build 
from urllib.parse import urlparse
from pathlib import Path
#done in google colab so using drive 
from google.colab import drive 
#mounting google drive to google colab 
drive.mount('/content/gdrive')
#importing OS to move between directorys in drive
import os
import time
import re
import pprint 
import json
import csv
import logging
import sys
import pandas as pd

# arguments to be passed to build function 
# Google Developer Key needed for YouTube Data API
DEVELOPER_KEY = "AIzaSyD3lX3yk9bWNNk1DcqKB6d-cMzLJsRhCPA" # pust your Google developer key here
#"AIzaSyAg2IZajtQ-GRF7AkIux2MMVAAk1eT_DKA"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class MemoryCache():
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content

# creating youtube resource object 
# for interacting with API 
youtube = build(YOUTUBE_API_SERVICE_NAME,  
                     YOUTUBE_API_VERSION, 
            developerKey = DEVELOPER_KEY,
               cache=MemoryCache())

def getVideosIds(path):
    ids = []
    videos = pd.read_csv(path)
    for i, row in videos.iterrows():
        ids.append(get_video_id(row['vid_url']))
    return ids

def getCurrentDirectory():
    return os.getcwd()

def getParentDirectory():
    return str(Path(os.getcwd()).parent)

def get_video_id(the_link):
    vid = re.findall('v(?:=|%3D)([^&%?]+)', urlparse(the_link).query)
    if vid:
        return vid[0]
    the_path = urlparse(the_link).path[1:]
    if ((not the_path) or 
        the_path.startswith('user') or 
        the_path.startswith('shared') or
        the_path.startswith('playlist') or
        the_path.startswith('channel') or 
        the_path.startswith('attribution_link') or 
        the_path.startswith('results') or 
        the_path.startswith('edit') or 
        the_path.startswith('categories') or 
        the_path.startswith('c/') or 
        the_path.startswith('view_play_list')): 
            return None
    if the_path.startswith('embed/'): return the_path[len('embed/'):len('embed/')+11]#typical length of the id
    if the_path.startswith('v/'): return the_path[len('v/'):len('v/')+11]
    
    return the_path

def jsonExists(vid_id, path):
    files_names = [ name for name in os.listdir(path) if name.startswith(vid_id) and not os.path.isdir(os.path.join(path, name)) ]
    return len(files_names) > 0

#results_dir_path is the directory for saving output
#results_file_path is the csv file for inputting that has youtube videos
results_dir_path = '/content/gdrive/Shared drives/allVideos/vids'
results_file_path = '1-10.csv'

def main():
    #changes the OS to be in the drive
    os.chdir('/content')
    counter = 0
    videos = []
    #retrieves all of the video IDS from the CSV file of YouTube videos
    ids = getVideosIds(results_file_path)
    
    #changes the directory to be in the output directory
    os.chdir('/content/gdrive/Shared drives/allVideos/vids')
    
    
    count = 0
    checkCount = 0
    
    
   
    #going through each video ID
    for vid_id in ids:
        
        videoList = []
        
        #calls the youtube.videos().list() method
        #to retrieve information on the videos
        list_videos_byid = youtube.videos().list(
          part="snippet",
          id=vid_id
          ).execute()
        
        #creates a list of that information
        results = list_videos_byid.get("items", [])
        
        #retrieves the channelID and the channelTitle from 
        #the information of a video
        for result in results:
           details = result['snippet']['channelId']
           channelName = result['snippet']['channelTitle']
  
        #checks to see if that channel has already been handled
        #from output directory
        if jsonExists(details, results_dir_path):
            continue
        else:
            #uses the channelID to call channels().list() method from
            #youTube data API to gather specific information
            getPlaylist = youtube.channels().list(
              part="contentDetails",
              id=details
              ).execute()
            
        
            resultsUpload = getPlaylist.get("items", [])
            #if the list isnt empty, grab some of the videos made by that channel
            if len(resultsUpload) != 0:
                for result2 in resultsUpload:
                    uploadId = result2['contentDetails']['relatedPlaylists']['uploads']
                #if there are still more videos to gather
                try:
                    #call playlistItems().list() method to gather even more of the 
                    #videos from the channel
                    all_Videos = youtube.playlistItems().list(
                      part="snippet",
                      maxResults = 50,
                      playlistId=uploadId
                      ).execute()
                      
                    #append the videos found to a videoList
                    videoList.append(all_Videos.get("items", []))
                    
                    #checks to see if there is a nextPageToken 
                    #meaning more videos can be found
                    while 'nextPageToken' in all_Videos:
                        all_Videos = youtube.playlistItems().list(
                          part="snippet",
                          maxResults = 50,
                          playlistId=uploadId,
                          pageToken = all_Videos['nextPageToken']
                          ).execute()
                        #gathers the rest of the videos and appends them to the list
                        videoList.append(all_Videos.get("items", []))
                except:
                    videoList.append("none")
                
                #checks to see if the list isn't empty then outputs 
                #all of the channel videos from the found channels of the youtube videos
                if(videoList[0] != "none"):
                    with open(channelName + '.json', 'w') as outfile:
                        json.dump(obj=videoList, indent=4, fp = outfile)
            
                
           
        
main()

print('Finished')

