import sys
from os import remove, write
from threading import Thread

#from gevent import sleep
from time import sleep
import requests
import bs4

from .config import IMAGE_CACHE, SINGLE_IMAGE_DELETE_AFTER_SECS

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
    orig_url = url
    if not url.startswith('https://imgur.com/'):
        url = 'https://imgur.com/' + url

    album = False
    if url.startswith("https://imgur.com/a/"):
        album = True
        if not url.endswith("blog"):
            url += "/layout/blog"


    if not album:
        print('Getting img', url)
        url = 'https://i.imgur.com/' + url.rsplit('/', 1)[-1]
        with open(f'{write_dir}/{url[-11:]}', 'wb') as img:
            img.write(requests.get(url).content)
        if delete:
            Thread(target=delete_file, args=[f"{write_dir}/{url[-11:]}"]).start()
        return None
    else:
        found_url = ''
        found_urls = []
        found_list_file = ''
        title = ''
        metas = []
        print('Detecting album/gallery images (contentUrl)', url)
        soup = bs4.BeautifulSoup(requests.get(url).text, 'html.parser')
        try:
            title = soup.select('meta[property="og:title"]')[0]['content']
            if title == "Imgur":
                title = ''
        except (KeyError, IndexError):
            title = ''
        for count, el in enumerate(soup.select('.post-image-container'), start=1):
            if el is None:
                continue
            minisoup = bs4.BeautifulSoup(str(el), 'html.parser')
            try:
                found_url = "https:" + minisoup.select('.post-image meta[itemprop="contentUrl"]')[0]['content']
                if '?1' in found_url:
                    continue
            except (KeyError, IndexError):
                error("Could not obtain url for detected image (contentUrl), trying id method")
                try:
                    found_url = "https://i.imgur.com/" + el['id'] + ".jpg" # equivalent to .png
                except KeyError:
                    error("Could not obtain url for detected image (id), trying reverse id method")
                    try:
                        found_url = "https://i.imgur.com/" + el['id'] + ".png" # equivalent to .png
                    except KeyError:
                        error("Could not obtain url for detected image (id)")
                        continue
            if found_url.endswith('ico.jpg'):
                continue
            found_urls.append(found_url[-11:])
            print(f"Downloading image {count}: {found_url}")

            print("Writing image", f"{write_dir}{found_url[-11:]}")
            with open(f"{write_dir}{found_url[-11:]}", "wb") as f:
                f.write(requests.get(found_url).content)

            if delete:
                Thread(target=delete_file, args=[f"{write_dir}{found_url[-11:]}"]).start()

            subtitle = ''
            try:
                subtitle = minisoup.select('.post-image-title')[0].string
            except IndexError:
                subtitle = ''
            desc = ''
            try:
                desc = minisoup.select('.post-image-description')[0].string
            except IndexError:
                desc = ''
            date = ''
            metas.append((subtitle, desc))
        # Write the found urls to a file with the name of the album so the viewer endpoint can get them
        found_list_file = write_dir + orig_url.replace('/', '_')
        with open(found_list_file, 'w') as f:
            f.write(','.join(found_urls))
        Thread(target=delete_file, args=[found_list_file]).start()
        return title, metas
