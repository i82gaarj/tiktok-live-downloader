# TikTok LIVE Downloader
Simple Python script to automatically download TikTok LIVE streams from specified users.

I did this because YT-DLP stops working when there is a change in TikTok API, so here I can fix it quickly. In this script, I only use YT-DLP to handle the filename and the download of the FLV stream.

NOTICE: It only works with public accounts for now.

<!--<div align="center">
  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![GitHub last commit](https://img.shields.io/github/last-commit/i82gaarj/tiktok-live-downloader?style=for-the-badge)
![GitHub repo size](https://img.shields.io/github/repo-size/i82gaarj/tiktok-live-downloader?style=for-the-badge)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/i82gaarj/tiktok-live-downloader?style=for-the-badge)

</div>-->

## Usage
Clone the repository:

```bash
git clone https://github.com/i82gaarj/tiktok-live-downloader.git
cd tiktok-live-downloader
```
Set configFilePath and destFilePath variables in the script (I will move this to a config file later)

Create a Python virtual env and install yt-dlp with pip in the same venv.
```bash
virtualenv -p /usr/bin/python3 tiktokvenv
cd tiktokvenv
source bin/activate
pip3 install yt-dlp
```

Now you can start the script with ```python3 downloadTikTokLIVE.py username```. If the user is live, it will start downloading the stream.

### Quality config file
There is an example config file to choose the download quality for every user/channel. If there is no config, it will download the stream in "SD1" (the lowest quality offered by TikTok), but you can change this in the script.

### Linux SystemD service
Recommended:
- Use a hosted server, home server or any Linux device that is always running.

In Linux, create a service template in ```/lib/systemd/system/your-tiktok-service@.service```:

```
[Unit]
Description=TikTok LIVE Downloader for user %I
[Service]
User=your-user ### SET THIS TO YOUR LINUX USER
Type=simple

ExecStart=-/path/to/venv/python /path/to/downloadTikTokLIVE.py %i ### SET THIS TO YOUR PATHS
Environment="PATH=/path/to/venv/python/bin/:/usr/bin" # you will need this if you use YT-DLP in a virtualenv

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```systemctl enable your-tiktok-service@channelname && systemctl start your-tiktok-service@channelname``` (may require root privileges)

Whenever the user starts streaming, the script will download the stream. Keep in mind that there is a 40-second delay between checks, so the download could start a bit later.

There will be one instance of the service for every channel/user. If there is an error, it will be logged in the system log.

The filename will be something like ```2024-01-01_13-16-28_[Stream title]_roomID_userID_[username].flv```.

This was tested on a Raspberry Pi 4B using Raspbian OS.

### Issues

- Sometimes the stream stops and starts multiple times due to bad network connection of the streamer. This will cause the stream to split into several files.

- Sometimes the stream stops in a wrong way causing YT-DLP to not rename the ".part" file. You can remove the .part extension but the video probably won't be seekable. You will need to use ffmpeg and copy the video to a new file without re-encoding to fix this.

- I've sometimes had problems with already downloaded FLV TikTok streams, specially when more users joined the stream. In these cases the video duration is totally incorrect (usually hundreds of hours). This is NOT an issue with this script.

## To do
- [ ] Refactor the code.
- [ ] Make some options configurable in another config file.
- [ ] Allow authentication so the user can download streams from private accounts.
- [ ] Allow using proxies to bypass login restrictions in some countries.

## Legal
This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by TikTok or any of its affiliates or subsidiaries. Use at your own risk.
