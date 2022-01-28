#!/usr/bin/python

import bs4
import json
import logging
import os

import database
from scrape import Scraper

cwd = os.path.dirname(os.path.realpath(__file__))


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
        logging.basicConfig(filename=f'{cwd}/logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

        with open(f'{cwd}/config.json') as f:
            self.config = json.load(f)
        self.parameters = self.config['met']['parameters']

    def _convert_wind_direction(self, direction: str):
        """Converts wind direction from str (SA) to int (135).

        Helper function for _get_data_by_parameter()

        Args:
            direction (str): The direction as a string

        Returns:
            (int): The corresponding wind direction as an int
        """

        directions = self.config['wind_directions']
        for direction_str, direction_int in directions.items():
            if direction_str == direction:
                return direction_int

    def _get_data_by_parameter(self, soup: bs4.BeautifulSoup, parameter: str):
        """Iteratively finds all appearances of parameter in soup.

        Helper method for parse()

        Args:
            soup (bs4.BeautifulSoup): The query results
            parameter (str): The parameter to be looked up in soup

        Returns:
            values_by_parameter (list): A list of all the values of
                the parameter key in soup
        """
        values_by_parameter = []
        for data_point in soup.find_all(parameter):
            if parameter == 'd':
                direction = self._convert_wind_direction(data_point.text)
                values_by_parameter.append(direction)
                continue
            values_by_parameter.append(data_point.text)

        return values_by_parameter

    def get_url(self, station_id: str):
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

    def parse(self, station_name: str, soup: bs4.BeautifulSoup):
        """Parses the raw, scraped data to desired format for SQL writing.

        Args:
            station_name (str): The station name (e.g. Grindavík)
            soup (bs4.BeautifulSoup): The query result

        Returns:
            (list): Nested tuples in a list with the formatted
                query results
        """

        NO_TIMESTEPS = len(soup.find_all("ftime"))
        parsed_data = list()
        for parameter in self.parameters:
            # The timestamp of when the forecast was made.
            # Is only given once so must be multiplied
            if parameter == 'atime':
                atime = soup.find(parameter)
                parsed_data.append([atime.text] * NO_TIMESTEPS)
                continue
            # Also must multiply the station name
            if parameter == 'station':
                parsed_data.append([station_name] * NO_TIMESTEPS)
                continue
            parsed_data.append(self._get_data_by_parameter(soup, parameter))

        return list(zip(*parsed_data))


def main():
    with open(f'{cwd}/config.json') as f:
        config = json.load(f)
    stations = config["met"]["stations"]
    weather = Forecast()
    sql = database.SQL()
    for station_name, station_id in stations.items():
        url = weather.get_url(station_id)
        with Scraper() as scrape_:
            raw_data = scrape_.scrape(url, 'weather')
        formatted_data = weather.parse(station_name, raw_data)
        sql.write(table='weather', data=formatted_data, NO_COLUMNS=8)


if __name__ == '__main__':
    main()
