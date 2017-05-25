#!/usr/bin/env python

# import libraries
import pixivpy3 # pip install pixivpy --upgrade
import feedgen # pip install feedgen
import time, sys, os
import os.path
from pixivpy3 import *
from feedgen.feed import FeedGenerator

SERVER_PATH = "yourserverpathhere"
FOLDER_PATH = "importfolderhere"

# number of illistrations that you might want pull from the pixiv API, 90 should be enough
NUM_ILLUST = 90

# here you insert your path for the cache folder, it is optimised for linux but if you have a windows device it should work just fine
os.chdir(FOLDER_PATH)

# handles reading the url, finds the img file, downloads it, adds it as an entry and add rss info
def handle_one_img_url(api, feed, url, illust):
  try:
    print("creating article for " + url)
    filename = url[url.rfind("/")+1:]
    if not os.path.isfile(filename):
      api.download(url)
    
    if not os.path.isfile(filename):
      raise Exception('Error in fetching')
    
    entry = feed.add_entry()
    entry.pubdate(illust.create_date)
    entry.id(filename)
    entry.enclosure(SERVER_PATH + filename, 0, 'image/jpeg')
    entry.title(illust.title)
    
    description = ""
    description += "<img src='" + SERVER_PATH + filename + "' />"
    description += "<h1><a href='https://www.pixiv.net/member_illust.php?id=" + str(illust.user.id) + "'>" + illust.user.name + "(" + str(illust.user.id) + ")" + "</a></h1>"
    description += "<h1><a href='https://www.pixiv.net/member_illust.php?mode=medium&illust_id=" + str(illust.id) + "'>" + illust.title + "</a></h1>"
    # conversion sometimes fails on weird characters
    try:
      description += illust.caption.encode("ascii")
    except:
      description += ""
    
    for tag in illust.tags:
      description += "<br />" + tag.name
    
    entry.description(description)
		
  except Exception as e:
    # don't forget to clean up the entry so that feedgenerator doesnt crash
    try:
      feed.remove_entry(entry)
    except:
      print("no entry to remove")
			
    print("ERRROR IN FETCHING", e)


def create_feed(username, password, feed_file_name):
  api = AppPixivAPI()
  api.login(username, password)
  print("auth success")
	
  feed = FeedGenerator()
  feed.id(SERVER_PATH + feed_file_name)
  feed.title('Pixiv Subscriber feed')
  feed.author( {'name':'Motaz Aljamal','email':'A13x7950@gmail.com'} )
  feed.link( href=SERVER_PATH + feed_file_name, rel='alternate' )
  feed.description('Pixiv Subscriber feed')

  offset = 0
  while offset < NUM_ILLUST:
    print("loop with offset " + str(offset))
    illusts = api.illust_follow(offset=offset)
    offset += len(illusts.illusts)
  
  for illust in illusts.illusts:
    print("new illust")
    if illust.page_count>1: # pixiv comic
      for page in range(0, illust.page_count-1):
      # we create one RSS entry by image in the comic
        handle_one_img_url(api, feed, illust.meta_pages[page].image_urls.medium, illust)
    else:
      handle_one_img_url(api, feed, illust.image_urls.medium, illust)

  feed.rss_file(FOLDER_PATH + feed_file_name)


def garbage_colector(days):
  now = time.time()
  for f in os.listdir("."):
    if os.stat(f).st_mtime < now - days * 86400:
      os.remove(f)




# example use
create_feed("user", "password", "feed.xml")
garbage_colector(30)
