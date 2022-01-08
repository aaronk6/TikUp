import os
import re
import shutil
import sys
import time
import random

from internetarchive import get_item, upload
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


def uploadTikTok(username, tiktok, deletionStatus, file):
    regex = re.compile('[0-9]{17}')
    regexA = re.compile('[0-9]{18}')
    regexB = re.compile('[0-9]{19}')
    regexC = re.compile('[0-9]{8}')
    regexD = re.compile('[0-9]{9}')
    if os.path.isdir(tiktok):
        if (
            regex.match(str(tiktok))
            or (regexA.match(str(tiktok)))
            or (regexB.match(str(tiktok)))
            or (regexC.match(str(tiktok)))
            or (regexD.match(str(tiktok)))
        ):  # TODO: use or regex with "|" instead of this
            item = get_item('tiktok-' + tiktok)
            if username is None:
                if file is not None:
                    file.write(str(tiktok))
                    file.write('\n')
                return None
            item.upload(
                './' + tiktok + '/',
                verbose=True,
                checksum=True,
                delete=deletionStatus,
                metadata=dict(
                    collection='opensource_media',
                    subject='tiktok',
                    creator=username,
                    title='TikTok Video by ' + username,
                    originalurl='https://www.tiktok.com/@' + username + '/video/' + tiktok,
                    scanner='TikUp ' + getVersion(),
                ),
                retries=9001,
                retries_sleep=60,
            )
            if deletionStatus:
                os.rmdir(tiktok)
            print()
            print('Uploaded to https://archive.org/details/tiktok-' + tiktok)
            print()
            if file is not None:
                file.write(str(tiktok))
                file.write('\n')


def downloadTikToks(username, tiktoks, file, downloadType, did):
    cwd = os.getcwd()
    try:
        lines = file.readlines()
        for x in range(0, len(lines)):
            lines[x] = lines[x].replace('\n', '')
    except:
        lines = ''
    ids = []
    for tiktok in tiktoks:
        if str(type(tiktok)) == '<class \'dict\'>':
            try:
                tiktok = tiktok['id']
            except KeyError:
                tiktok = tiktok['itemInfos']['id']
        if file is not None and doesIdExist(lines, tiktok):
            print(tiktok + " has already been archived.")
        else:
            tiktokObj = getTikTokObject(tiktok, did)
            if not tiktokObj:
                ids.append(tiktok)
                continue
            username = getUsername(tiktok)
            if username is None:
                print(tiktok + ' has been deleted or is private')
                ids.append(tiktok)
            else:
                downloadTikTok(username, tiktokObj, cwd, 1, did)
                i = 1
                while not os.path.exists(tiktok + '/' + tiktok + '.mp4'):
                    tiktokObj = getTikTokObject(tiktok, did)
                    username = getUsername(tiktok)
                    time.sleep(1)
                    downloadTikTok(username, tiktokObj, cwd, i, did)
                    i += 1
            ids.append(tiktok)
    return ids


def uploadTikToks(tiktoks, file, delete):
    for tiktok in tiktoks:
        uploadTikTok(getUsername(tiktok), tiktok, delete, file)


def doesIdExist(lines, tiktok):
    return tiktok in lines


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
    delete = args.no_delete
    limit = args.limit
    archive = args.use_download_archive
    folder = args.folder
    global upload
    upload = args.no_upload

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
    if archive:
        try:
            file = open('archive.txt', 'r+')
        except FileNotFoundError:
            f = open('archive.txt', 'x')
            f.close()
            file = open('archive.txt', 'r+')
    else:
        file = None
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
    tiktoks = downloadTikToks(username, tiktoks, file, downloadType, did)
    if upload == True:
        uploadTikToks(tiktoks, file, delete)

    try:
        for tiktok_id in tiktoks:
            file.write(tiktok_id + '\n')
        file.close()
    except:
        pass
    print('')


if __name__ == "__main__":
    main()
