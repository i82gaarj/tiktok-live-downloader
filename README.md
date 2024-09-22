# TikTok LIVE Downloader
Simple Python script for downloading TikTok LIVE streams.

I did this because YT-DLP stops working when there is a change in TikTok API, so I can fix it quickly.

## Tutorial
Required: [yt-dlp](https://github.com/yt-dlp/yt-dlp) installed

Recommended: create a Python virtual env and install yt-dlp in the same venv.

### Formats config file
There is an example config file to choose the download quality for every user/channel. If there is no config, it will download in "SD1" (the lowest quality offered by TikTok), but you can change this in the script.

### Service
In Linux, create a service template in ```/lib/systemd/system/your-tiktok-service@.service```:

```
[Unit]
Description=TikTok LIVE Downloader for user %I
[Service]
User=your-user
Type=simple

ExecStart=-/path/to/venv/python /path/to/downloadTikTokLIVE.py %i
Environment="PATH=/path/to/venv/python/bin/:/usr/bin" # you will need this if you use YT-DLP in a virtualenv

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```systemctl enable your-tiktok-service@channelname && systemctl start your-tiktok-service@channelname```

There will be one instance of the service for every channel.
If there is an error, it will be logged on the system log.
