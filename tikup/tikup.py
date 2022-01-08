import os
import re
import shutil
import sys
import time
import random

from TikTokApi import TikTokApi
#Make sure to change to 'from .argparser import parse_args' when uploading
from .argparser import parse_args


api = TikTokApi()


def getVersion():
    return '2021.08.24'


def getUsernameVideos(username, limit):
    if limit is not None:
        count = int(limit)
    else:
        count = 9999
    tiktoks = api.by_username(username, count=count)
    return tiktoks


def getHashtagVideos(hashtag, limit):
    if limit is not None:
        count = int(limit)
    else:
        count = 9999
    tiktoks = api.by_hashtag(hashtag, count=count)
    return tiktoks


def getLikedVideos(username, limit):
    if limit is not None:
        count = int(limit)
    else:
        count = 9999
    tiktoks = api.user_liked_by_username(username, count=count)
    return tiktoks

def downloadTikTok(username, tiktok, cwd, varTry, did):
    try:
        tiktokID = tiktok['id']
    except:
        try:
            tiktokID = tiktok['itemInfos']['id']
        except:
            tiktokID = tiktok['itemInfo']['itemStruct']['id']
    if not os.path.exists(tiktokID):
        os.mkdir(tiktokID)
    os.chdir(tiktokID)
    if (os.path.exists(tiktokID + '.mp4') and os.path.getsize(tiktokID + '.mp4') > 0) and (os.path.exists('tiktok_info.json') and os.path.getsize('tiktok_info.json') > 0):
        print("%s already exists, not going to redownload" % tiktokID)
    else:
        print("Downloading TikTok %s from %s" % ( tiktokID, tiktok['itemInfo']['itemStruct']['video']['downloadAddr'] ))
        mp4 = open(tiktokID + '.mp4', "wb")
        mp4.write(api.get_video_by_download_url(tiktok['itemInfo']['itemStruct']['video']['downloadAddr'], custom_did=did))
        mp4.close()
            #shutil.rmtree('tmp')
        json = open("tiktok_info.json", "w", encoding="utf-8")
        json.write(str(tiktok))
        json.close()
    os.chdir(cwd)


def downloadTikToks(username, tiktoks, downloadType, did):
    print("Downloading %s TikTok(s)" % len(tiktoks))
    cwd = os.getcwd()
    for tiktok in tiktoks:
        if str(type(tiktok)) == '<class \'dict\'>':
            try:
                tiktok = tiktok['id']
            except KeyError:
                tiktok = tiktok['itemInfos']['id']

        tiktokObj = getTikTokObject(tiktok, did)
        if not tiktokObj:
            continue
        username = getUsername(tiktok)

        if username is None:
            print(tiktok + ' has been deleted or is private')
            continue

        downloadTikTok(username, tiktokObj, cwd, 1, did)
        i = 1
        while not os.path.exists(tiktok + '/' + tiktok + '.mp4'):
            tiktokObj = getTikTokObject(tiktok, did)
            username = getUsername(tiktok)
            time.sleep(1)
            downloadTikTok(username, tiktokObj, cwd, i, did)
            i += 1


def getUsername(tiktokId):
    thing = api.get_tiktok_by_id(tiktokId)
    try:
        return thing['itemInfo']['itemStruct']['author']['uniqueId']
    except:
        return None


def getTikTokObject(tiktokId, did):
    tries = 5
    thing = None
    for i in range(tries):
        try:
            thing = api.get_tiktok_by_id(tiktokId, custom_did=did)
        except Exception as e:
            if i < tries - 1:
                print("Got an exception (%s) when trying to get TikTok %s, retrying..." % (e, tiktokId))
                time.sleep(1)
                continue
            else:
                print("Giving up - %s was NOT downloaded!" % tiktokId)
        break
    return thing


def main():
    args = parse_args()
    username = args.user
    limit = args.limit
    folder = args.folder

    if folder == None:
        os.chdir(os.path.expanduser('~'))
        if not os.path.exists('./.tikup'):
            os.mkdir('./.tikup')
        os.chdir('./.tikup')
    else:
        if not os.path.exists(folder):
            os.mkdir(folder)
        os.chdir(folder)

    downloadType = ''
    did = str(random.randint(10000, 999999999))
    if args.hashtag:  # Download hashtag
        downloadType = 'hashtag'
        tiktoks = getHashtagVideos(username, limit)
    elif args.id:  # Download user ID
        downloadType = 'id'
        tiktoks = [username]
    elif args.liked:  # Download liked
        downloadType = 'liked'
        tiktoks = getLikedVideos(username, limit)
    else:  # Download username
        downloadType = 'username'
        tiktoks = getUsernameVideos(username, limit)
    tiktoks = downloadTikToks(username, tiktoks, downloadType, did)

    print('')


if __name__ == "__main__":
    main()
