import bs4
from bs4 import BeautifulSoup
import json
import logging
import requests
import traceback

import database


class Forecast:
    """Scrapes meteorological forecasts.

    Scrapes weather forecasts from The Met's XML-service,
    formats, and finally saves to a SQL database.

    List of station IDs:
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

    def _get_url(self, station_id: str):
        """Gets the URL for the MET query.

        Helper function for scrape()

        Args:
            station_id (str): The station ID (see class description)

        Returns:
            (str): The URL
        """        
        url_prefix = self.config['met']['url_prefix']
        url_appendix = self.config['met']['url_appendix']

        return f'{url_prefix}{station_id}{url_appendix}'

    def _convert_wind_direction(self, direction: str):
        """Converts wind direction from str (SA) to int (135).

        Helper function for parse()

        Args:
            direction (str): The direction as a string

        Returns:
            (int): The corresponding wind direction as an int
        """        

        directions = self.config['wind_directions']
        for direction_str, direction_int in directions.items():
            if direction_str == direction:
                return direction_int

    def scrape(self, station_id: str):
        """Scrapes weather forecasts from Icelandic Met.

        Stations and parameters configured in config.json.

        Args:
            station_id (str): The station ID (see class description)

        Returns:
            (bs4.BeautifulSoup): The query results
        
        Raises:
            requests.exceptions.ConnectionError: If connection isn't made
        """

        url = self._get_url(station_id)
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            # TODO: Raise different requests exception
            raise requests.exceptions.ConnectionError

        return BeautifulSoup(r.content, 'html.parser')

    def parse(self, station_name: str, raw_data: bs4.BeautifulSoup):
        """Parses the raw, scraped data to desired format for SQL writing.

        Args:
            station_name (str): The station name (e.g. Grindavík)
            raw_data (bs4.BeautifulSoup): The query result

        Returns:
            (list): Nested tuples in a list with the formatted
                query results
        """

        NO_TIMESTEPS = len(raw_data.find_all("ftime"))
        parsed_data = list()
        for parameter in self.parameters:
            # The timestamp of when the forecast was made.
            # Is only given once so must be multiplied
            if parameter == 'atime':
                atime = raw_data.find(parameter)
                parsed_data.append([atime.text] * NO_TIMESTEPS)
                continue
            # Also must multiply the station name
            if parameter == 'station':
                parsed_data.append([station_name] * NO_TIMESTEPS)
                continue
            data_points_by_parameter = []
            for data_point in raw_data.find_all(parameter):
                if parameter == 'd':
                    direction = self._convert_wind_direction(
                        data_point.text)
                    data_points_by_parameter.append(direction)
                else:
                    data_points_by_parameter.append(data_point.text)
            parsed_data.append(data_points_by_parameter)

        return list(zip(*parsed_data))


def main():
    with open('config.json') as f:
        config = json.load(f)
    stations = config["met"]["stations"]
    weather = Forecast()
    sql = database.SQL()
    for station_name, station_id in stations.items():
        raw_data = weather.scrape(station_id)
        formatted_data = weather.parse(station_name, raw_data)
        sql.write(table='weather', data=formatted_data, NO_COLUMNS=8)


if __name__ == '__main__':
    main()
