import unittest
import os
from glob import glob

from imgin import get

CACHE_DIR = '/tmp/imgin-imgur-images-album/'

class TestAlbum(unittest.TestCase):

    def test_album_a(self):
        code = 'ethCwFv'
        get(f"https://imgur.com/a/{code}", CACHE_DIR)
        files = glob(CACHE_DIR + '*')
        for i in files:
            if i.endswith('m_a_ethCwFv'):
                continue
            print(f'got tests/test_images/album/{i[-11:]} checking if it is an image we should have')
            self.assertTrue(os.path.exists(f'tests/test_images/album/{i[-11:]}'))

try:
    os.mkdir(CACHE_DIR)
except FileExistsError:
    pass

unittest.main()