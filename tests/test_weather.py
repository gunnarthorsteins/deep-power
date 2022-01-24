import os
import sys
# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)

from weather import Forecast
from scrape import Scraper
import unittest

url = 'https://xmlweather.vedur.is/?op_w=xml&type=forec&lang=en&view=xml&ids=1361&params=F;D;T;N;R&time=1h'


class TestWeather(unittest.TestCase):
    def test_instance(self):
        forecast_ = Forecast()
        self.assertIsInstance(forecast_, Forecast)

    def test_scrape(self):
        with Scraper() as scrape_:
            soup = scrape_.scrape(url=url)
        self.assertIsNotNone(soup)

    def test_parse(self):
        forecast_ = Forecast()
        with Scraper() as scrape_:
            soup = scrape_.scrape(url=url)
        formatted_forecasts = forecast_.parse(
            station_name='Grindavík', soup=soup
        )
        self.assertIsNotNone(formatted_forecasts)


if __name__ == "__main__":
    unittest.main()
