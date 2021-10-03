import sys
from shutil import rmtree
from os import remove
from threading import Thread

import requests
import bs4
from gevent import sleep

from .config import SINGLE_IMAGE_DELETE_AFTER_SECS, ALBUM_DELETE_AFTER_SECS

def delete_file(path):
    sleep(SINGLE_IMAGE_DELETE_AFTER_SECS)
    print('Erasing', path)
    try:
        remove(path)
    except FileNotFoundError:
        pass


def error(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()

def get(url: str, write_dir: str, delete=True):
    if not url.startswith('https://imgur.com/'):
        url = 'https://imgur.com/' + url
    found_url = ''

    album = False
    if "gallery" in url:
        url = url.replace("gallery", "a")
    if "/a/" in url:
        album = True
        if not url.endswith("blog"):
            url += "/layout/blog"
    else:
        if url.endswith("jpeg") and not url.endswith("jpg") and not url.endswith("png"):
            url += ".jpg"


    if not album:
        print('Getting img', url)
        url = 'https://i.imgur.com/' + url.rsplit('/', 1)[-1].replace('jpeg', 'jpg')
        with open(f'{write_dir}/{url[-11:]}', 'wb') as img:
            img.write(requests.get(url).content)
        if delete:
            Thread(target=delete_file, args=[f"{write_dir}/{url[-11:]}"]).start()
    else:
        print('Detecting album/gallery images', url)
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
        for count, el in enumerate(soup.select('.post-image meta[itemprop="contentUrl"]'), start=1):
            try:
                found_url = "https:" + el['content']
            except KeyError:
                error("Could not obtain url for detected image")
                continue
            print(f"Downloading image {count}: {found_url}")

            print("Writing image", f"{write_dir}{found_url[-11:]}")
            with open(f"{write_dir}{found_url[-11:]}", "wb") as f:
                f.write(requests.get(found_url).content)
            if delete:
                Thread(target=delete_file, args=[f"{write_dir}{found_url[-11:]}"]).start()

