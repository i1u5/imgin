from gevent import monkey
from gevent import sleep
monkey.patch_all()
from threading import Thread
from os import remove, mkdir, path, stat
from shutil import rmtree
from glob import glob

from uuid import uuid4

from bottle import route, run
from bottle import static_file
from bottle import SimpleTemplate

from .get import get
from .config import IMAGE_CACHE, SINGLE_IMAGE_DELETE_AFTER_SECS, ALBUM_DELETE_AFTER_SECS, template_dir


def get_timestamp_of_file(file):
    return stat(file).st_ctime

def album(id):
    req_id = str(uuid4())
    req = IMAGE_CACHE

    get("/a/" + id, req)

    imgs = glob(req + "*")

    # sort image order (file creation time)
    imgs = sorted(imgs, key=get_timestamp_of_file)

    for c, img in enumerate(imgs):
        imgs[c] = img.replace(IMAGE_CACHE, '/')



    with open(f'{template_dir}gallery.html', 'r') as img_view:
        tpl = SimpleTemplate(img_view)
    return tpl.render(imgs=imgs)

@route('/')
@route('')
def home():
    return static_file("index.html", root=template_dir)

@route('/static/<file>')
def static(file=''):
    return static_file(file, root=template_dir)


@route('/gallery/<id>')
def gallery(id=''):
    return album(id)

@route('/a/<id>')
def gallery(id=''):
    return album(id)


@route('/<img>')
def hello(img=''):

    if not path.exists(IMAGE_CACHE + img):
        get(img, IMAGE_CACHE)
    return static_file(img, root=IMAGE_CACHE)


def start_server():
    try:
        rmtree(IMAGE_CACHE)
    except FileNotFoundError:
        pass
    mkdir(IMAGE_CACHE)

    run(server='gevent', host='0.0.0.0')