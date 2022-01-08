TikUp
=====

An auto downloader for TikTok videos.

**Requirements**  
[TikTok-Api](https://github.com/davidteather/TikTok-Api) and [playwright](https://github.com/Microsoft/playwright-python) on Python 3.

**How to Install**  
Install with `pip install tikup`.
Update with `pip install -U tikup`.

**How to Use**
```
usage: tikup [-h] [--hashtag] [--limit LIMIT] [--id] [--liked] [--folder FOLDER] [--no-upload] user

An auto downloader for TikTok videos.

positional arguments:
  user

optional arguments:
  -h, --help            show this help message and exit
  --hashtag             download this hashtag
  --limit LIMIT         set limit on amount of TikToks to download
  --id                  download this video ID
  --liked               download this user's liked posts
  --folder FOLDER       set download destination (default: ~/.tikup)
```
