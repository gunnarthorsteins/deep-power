import os
import sys
# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)


from weather import Forecast
import unittest


stations_validation = ['Grindavík',
                       "Vestmannaeyjar", "Hafnarfjörður", "Keflavík"]


class TestWeather(unittest.TestCase):
    def test_instance(self):
        forecast_ = Forecast()
        self.assertIsInstance(forecast_, Forecast)

    def test_scrape(self):
        forecast_ = Forecast()
        self.forecasts = forecast_.scrape()
        for i, (station, soup) in enumerate(self.forecasts.items()):
            self.assertEqual(station, stations_validation[i])
            self.assertIsNotNone(soup)

    # def test_parse(self):
        # formatted_forecasts = forecast_.parse(self.forecasts)
        # self.assert

    def test_write_to_db(self):
        pass


if __name__ == "__main__":
    unittest.main()
