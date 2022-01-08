from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description="An auto downloader and uploader for TikTok videos.")
    parser.add_argument("user")
    parser.add_argument(
        "--no-delete", action="store_false", help="don't delete files once uploaded to the Internet Archive"
    )
    parser.add_argument(
        "--hashtag", action="store_true", help="download this hashtag"
    )
    parser.add_argument(
        "--limit", help="set limit on amount of TikToks to download"
    )
    parser.add_argument(
        "--id", action="store_true", help="download this video ID"
    )
    parser.add_argument(
        "--liked", action="store_true", help="download this user's liked posts"
    )
    parser.add_argument(
        "--folder", help="set download destination (default: ~/.tikup)"
    )
    args = parser.parse_args()
    return args
