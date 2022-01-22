import os
import sys
# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)

from weather import Forecast
import unittest


class TestWeather(unittest.TestCase):
    def test_instance(self):
        forecast_ = Forecast()
        self.assertIsInstance(forecast_, Forecast)

    def test_scrape(self):
        forecast_ = Forecast()
        soup = forecast_.scrape(station_id=1361)
        self.assertIsNotNone(soup)

    def test_parse(self):
        forecast_ = Forecast()
        soup = forecast_.scrape(station_id=1361)
        formatted_forecasts = forecast_.parse(station_name='Grindavík', raw_data=soup)
        self.assertIsNotNone(formatted_forecasts)


if __name__ == "__main__":
    unittest.main()
