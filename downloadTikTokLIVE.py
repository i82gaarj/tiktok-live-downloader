import requests
import time
import subprocess
import json
import re
import sys
import shlex
from systemd import journal
import traceback
import random
from dotenv import load_dotenv
import os

# I set these wait times to avoid being blocked by TikTok's servers
TIME_WAIT_SHORT_SECS = 5
TIME_WAIT_NORMAL_SECS = 40
TIME_WAIT_LONG_SECS = 300
TIMEOUT_SECS = 8

channelName = sys.argv[1]
user_agents = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0'
]

urlWebpage = 'https://www.tiktok.com/@' + channelName + '/live'
urlApiRoomInfo = 'https://www.tiktok.com/api/live/detail/?aid=1988&roomID='
urlWebcast = 'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id='

configFilePath = '/path/to/your/channel/formats.txt'
destFilePath = '/path/to/your/channel/streams/'

while True:
    exception = None
    try:
        headers = {'User-Agent': random.choice(user_agents)} # Optional

        try:
            r1 = requests.get(urlWebpage, timeout=TIMEOUT_SECS, headers=headers)
            statusCodeR1 = r1.status_code
        except Exception as e:
            exception = e
            statusCodeR1 = None
        # Step 1: Load page contents
        if statusCodeR1 != None:
            try:
                contentsWebpage = r1.text
                roomIDstr = re.findall('roomId":"\d+', str(contentsWebpage)) # Get room IDs
                if len(roomIDstr) > 0:
                    roomID = roomIDstr[0][9:]
                else:
                    roomID = None
                    exception = None
            except Exception as e:
                exception = e
                roomID = None
            # Step 2: Get API room info
            if roomID != None:
                try:
                    r2 = requests.get(urlApiRoomInfo + str(roomID), timeout=TIMEOUT_SECS, headers=headers)
                    statusCodeR2 = r2.status_code
                except Exception as e:
                    exception = e
                    statusCodeR2 = None
                # Load API data
                if statusCodeR2 != None:
                    # Get Live status
                    try:
                        contentsApiRoomInfo = r2.text
                        jsonApiData = json.loads(contentsApiRoomInfo)
                        if "LiveRoomInfo" in jsonApiData and "status" in jsonApiData["LiveRoomInfo"]:
                            liveStatus = jsonApiData["LiveRoomInfo"]["status"]
                        else:
                            liveStatus = None
                            exception = None
                    except Exception as e:
                        exception = e
                        liveStatus = None
                    # Step 3: Check Live status
                    if liveStatus != None:
                        if liveStatus > 0 and liveStatus < 4: # 2 means live, 4 means offline, rarely I got 1 and 3 and probably mean live paused but I'm not sure
                            try:
                                fileExists = os.path.isfile(configFilePath)
                                if fileExists:
                                    load_dotenv(dotenv_path=configFilePath, override=True)
                                    quality = os.getenv(channelName) or 'sd1' # I set SD1 as default, other qualities are SD2/HD1/FULL_HD1/ORIGIN but don't change it because some low quality streams don't have them
                                else:
                                    quality = 'sd1'
                            except Exception as e:
                                quality = 'sd1'
                                log = journal.stream('TikTok Live - ' + channelName)
                                log.write('Warning: Couldn\'t get quality from config file. Using default \'sd1\'. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + '. ' + type(e).__name__ + ': ' + str(e) + '\n')
                            # Step 4: Get Room info and stream URL
                            try:
                                r3 = requests.get(urlWebcast + str(roomID), timeout=TIMEOUT_SECS, headers=headers)
                                statusCodeR3 = r3.status_code
                            except Exception as e:
                                exception = e
                                statusCodeR3 = None
                            if statusCodeR3 != None:
                                try:
                                    contentsApiWebcast = r3.text
                                    jsonApiWebcast = json.loads(contentsApiWebcast)
                                    if "data" in jsonApiWebcast:
                                        if quality == "origin":
                                            livestreamUrl = jsonApiWebcast["data"]["stream_url"]["rtmp_pull_url"] # URL for ORIGIN quality is in another JSON key
                                        else:
                                            qualityUppercase = quality.upper()
                                            livestreamUrl = jsonApiWebcast["data"]["stream_url"]["flv_pull_url"][qualityUppercase]
                                        if "title" in jsonApiWebcast["data"]:
                                            title = jsonApiWebcast["data"]["title"]
                                        else:
                                            title = 'NA'
                                    else:
                                        livestreamUrl = None
                                        exception = None
                                except Exception as e:
                                    exception = e
                                    livestreamUrl = None
                                if livestreamUrl != None:
                                    # Log
                                    log = journal.stream('TikTok Live - ' + channelName)
                                    log.write('Room ID: ' + str(roomID) + ', Live Status: ' + str(liveStatus) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + ', SC3: ' + str(statusCodeR3) + '\n')
                                    log.write('Starting livestream download...\n')
                                    # Download
                                    cmd = "yt-dlp --no-check-certificates " + livestreamUrl + ' -P ' + destFilePath + channelName + ' --no-overwrites -R 0 -o "%(epoch>%Y-%m-%d_%H-%M-%S)s_[' + title + ']_' + str(roomID) + '_' + str(jsonApiWebcast["data"]["owner_user_id"]) + '_[' + channelName + '].%(ext)s"'
                                    subprocess.run(shlex.split(cmd))
                                    log.write('Download finished\n')
                                else:
                                    log = journal.stream('TikTok Live - ' + channelName)
                                    if exception != None:
                                        log.write('Error 105: Couldn\'t get Livestream URL. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + ', SC3: ' + str(statusCodeR3) + '. ' + type(exception).__name__ + ': ' + str(exception) + '\n')
                                    else:
                                        log.write('Error 105: Couldn\'t get Livestream URL. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + ', SC3: ' + str(statusCodeR3) + '\n')
                                time.sleep(TIME_WAIT_SHORT_SECS)
                            else:
                                log = journal.stream('TikTok Live - ' + channelName)
                                log.write('Error 104: Couldn\'t get webcast info. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + ', SC3: ' + str(statusCodeR3) + '. ' + type(e).__name__ + ': ' + str(e) + '\n')
                                time.sleep(TIME_WAIT_NORMAL_SECS)
                        else: # Live OFF
                            # Log
                            log = journal.stream('TikTok Live - ' + channelName)
                            log.write('Room ID: ' + str(roomID) + ', Live Status: ' + str(liveStatus) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + '\n')
                            time.sleep(TIME_WAIT_NORMAL_SECS)
                    else:
                        log = journal.stream('TikTok Live - ' + channelName)
                        if exception != None:
                            log.write('Error 103: Couldn\'t get Live Status. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + '. ' + type(exception).__name__ + ': ' + str(exception) + '\n')
                        else:
                            log.write('Error 103: Couldn\'t get Live Status. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + ', SC2: ' + str(statusCodeR2) + '\n')
                        time.sleep(TIME_WAIT_NORMAL_SECS)
                else:
                    log = journal.stream('TikTok Live - ' + channelName)
                    log.write('Error 102: Couldn\'t get web API room info. Room ID: ' + str(roomID) + ', SC1: ' + str(statusCodeR1) + '. ' + type(exception).__name__ + ': ' + str(exception) + '\n')
                    time.sleep(TIME_WAIT_NORMAL_SECS)
            else:
                log = journal.stream('TikTok Live - ' + channelName)
                if exception != None:
                    log.write('Error 101: Couldn\'t get Room ID. SC1: ' + str(statusCodeR1) + '. ' + type(exception).__name__ + ': ' + str(exception) + '\n')
                else:
                    log.write('Error 101: Couldn\'t get Room ID. SC1: ' + str(statusCodeR1) + '\n')
                time.sleep(TIME_WAIT_NORMAL_SECS)
        else:
            log = journal.stream('TikTok Live - ' + channelName)
            log.write('Error 100: Couldn\'t get web page. ' + type(exception).__name__ + ': ' + str(exception) + '\n')
            time.sleep(TIME_WAIT_NORMAL_SECS)

    except Exception as e:
        log = journal.stream('TikTok Live - ' + channelName)
        log.write("Unknown exception: " + type(e).__name__ + ': ' + str(e))
        traceback.print_exc()
        time.sleep(TIME_WAIT_LONG_SECS) # Optional, you can set another time to wait
