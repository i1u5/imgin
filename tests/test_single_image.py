import unittest
import os

from imgin import get

CACHE_DIR = '/tmp/imgin-imgur-images-single/'

class TestSingleImage(unittest.TestCase):

    def test_single_image(self):
        img = "7TiLluI.jpg"
        get(f"https://imgur.com/{img}", CACHE_DIR)
        with open(f"tests/test_images/{img}", "rb") as expected:
            with open(CACHE_DIR + img, "rb") as actual:
                self.assertEqual(actual.read(), expected.read())

try:
    os.mkdir(CACHE_DIR)
except FileExistsError:
    pass

unittest.main()