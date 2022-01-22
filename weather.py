import bs4
from bs4 import BeautifulSoup
import fire
import json
import logging
import requests
import traceback

import database


class Forecast:
    """Scrapes meteorological forecasts.

    Scrapes weather forecasts from The Met's XML-service,
    formats, and finally saves to a SQL database.

    List of station codes:
    https://www.vedur.is/vedur/stodvar

    XML-service docs for additional query parameters:
    https://www.vedur.is/media/vedurstofan/XMLthjonusta.pdf
    """

    def __init__(self):
        logging.basicConfig(filename='logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

        with open('config.json') as f:
            self.config = json.load(f)

        self.parameters = self.config['met']['parameters']

    def _set_url(self, station_id: str):
        url_prefix = self.config['met']['url_prefix']
        url_appendix = self.config['met']['url_appendix']

        return f'{url_prefix}{station_id}{url_appendix}'

    def scrape(self, station_id: str):
        """Scrapes weather forecasts from Icelandic Met.

        Stations and parameters configured in config.json
        """

        url = self._set_url(station_id)
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            # TODO: Raise different requests exception
            raise requests.exceptions.Timeout

        return BeautifulSoup(r.content, 'html.parser')

    def parse(self, station_name: str, raw_data: bs4.BeautifulSoup):
        """Parses the raw, scraped data.

        Args:
            scraped_data (dict): The scraped data. Keys are station names,
                vals are the XML files

        Returns:
            formatted_data (pd.DataFrame): A relational-database-style
                version of the scraped data. 
        """

        NO_TIMESTEPS = len(raw_data.find_all("ftime"))
        parsed_data_by_station = []
        column_headers = []
        for parameter in self.parameters:
            column_headers.append(parameter)
            if parameter == 'atime':
                atime = raw_data.find(parameter)
                parsed_data_by_station.append([atime.text] * NO_TIMESTEPS)
            elif parameter == 'station':
                parsed_data_by_station.append(
                    [station_name] * NO_TIMESTEPS)
            else:
                data_points_by_parameter = []
                for data_point in raw_data.find_all(parameter):
                    if parameter == 'd':
                        direction = self._convert_wind_direction(
                            data_point.text)
                        data_points_by_parameter.append(direction)
                    else:
                        data_points_by_parameter.append(data_point.text)
                parsed_data_by_station.append(data_points_by_parameter)
        parsed_data = list(zip(*parsed_data_by_station))

        return parsed_data

    def _convert_wind_direction(self, direction: str):
        directions = self.config['wind_directions']
        for str_, val in directions.items():
            if str_ == direction:
                return val


def main():
    # try:
    with open('config.json') as f:
        config = json.load(f)
    stations = config["met"]["stations"]
    weather = Forecast()
    sql = database.SQL()
    for station_name, station_id in stations.items():
        raw_data = weather.scrape(station_id)
        formatted_data = weather.parse(station_name, raw_data)
        sql.write(table='weather', data=formatted_data, NO_COLUMNS=8)
    # except:
    #     logging.error(traceback.format_exc())


if __name__ == '__main__':
    fire.Fire(main)
