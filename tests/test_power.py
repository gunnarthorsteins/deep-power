import unittest
import os
import sys

# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)

from power import Landsnet
from scrape import Scraper


url = 'https://amper.landsnet.is/MapData/api/measurements'
filename = 'landsnet.html'

class TestWeather(unittest.TestCase):
    def test_instance(self):
        landsnet = Landsnet()
        self.assertIsInstance(landsnet, Landsnet)

    def test_scrape(self):
        with Scraper() as scrape_:
            soup = scrape_.scrape(url)
        self.assertIsNotNone(soup)
    
    def test_parse(self):
        landsnet = Landsnet()
        soup = landsnet.read_html()
        parsed_data = landsnet.parse(soup=soup)
        self.assertIsNotNone(parsed_data)


if __name__ == "__main__":
    unittest.main()
