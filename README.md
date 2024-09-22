# TikTok LIVE Downloader
Simple Python script for downloading TikTok LIVE streams.

I did this because YT-DLP stops working when there is a change in TikTok API, so here I can fix it quickly.

## Tutorial
Required: [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed.

Recommended:
- Create a Python virtual env and install yt-dlp with pip in the same venv.
- Use a hosted server, home server or any Linux device which is always running.

### Quality config file
There is an example config file to choose the download quality for every user/channel. If there is no config, it will download the stream in "SD1" (the lowest quality offered by TikTok), but you can change this in the script.

### Linux SystemD service
In Linux, create a service template in ```/lib/systemd/system/your-tiktok-service@.service```:

```
[Unit]
Description=TikTok LIVE Downloader for user %I
[Service]
User=your-user ### SET THIS TO YOUR USERNAME
Type=simple

ExecStart=-/path/to/venv/python /path/to/downloadTikTokLIVE.py %i ### SET THIS TO YOUR PATHS
Environment="PATH=/path/to/venv/python/bin/:/usr/bin" # you will need this if you use YT-DLP in a virtualenv

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```systemctl enable your-tiktok-service@channelname && systemctl start your-tiktok-service@channelname``` (may require root privileges).

Whenever the user starts streaming, the script will download the stream. Sometimes the stream stops and starts multiple times due to bad network connection of the streamer. This will split the stream into several files.

You can start manually the script with ```python3 downloadTikTokLIVE.py username```.

There will be one instance of the service for every channel. If there is an error, it will be logged on the system log.

The filename will be something like ```2024_01_01_[Stream title]_roomID_userID_[username].flv```.

This was tested on a Raspberry Pi 4B using Raspbian OS.
