from lib2to3.pgen2.pgen import DFAState
import fire
import json
import requests
import logging
import pandas as pd
import traceback
from datetime import datetime
from bs4 import BeautifulSoup

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

    def scrape(self):
        """Scrapes weather forecasts from Icelandic Met.

        Stations and parameters configured in config.json
        """

        stations = self.config['met']['stations']
        url_prefix = self.config['met']['url_prefix']
        url_appendix = self.config['met']['url_appendix']
        forecasts = dict()
        for name, id in stations.items():
            url = f'{url_prefix}{id}{url_appendix}'
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                raise requests.exceptions.Timeout
            soup = BeautifulSoup(r.content, 'html.parser')
            forecasts[name] = soup

        return forecasts

    def parse(self, raw_data: dict):
        """Parses the raw, scraped data.

        Args:
            scraped_data (dict): The scraped data. Keys are station names,
                vals are the XML files

        Returns:
            formatted_data (pd.DataFrame): A relational-database-style
                version of the scraped data. 
        """

        parameters = self.config['met']['parameters']
        all_data = []
        for station_name, data_by_station in raw_data.items():
            NO_TIMESTEPS = len(data_by_station.find_all("ftime"))
            parsed_data_by_station = []
            column_headers = []
            for parameter in parameters:
                column_headers.append(parameter)
                if parameter == 'atime':
                    atime = data_by_station.find(parameter)
                    parsed_data_by_station.append([atime.text] * NO_TIMESTEPS)
                elif parameter == 'station':
                    parsed_data_by_station.append(
                        [station_name] * NO_TIMESTEPS)
                else:
                    data_points_by_parameter = []
                    for data_point in data_by_station.find_all(parameter):
                        data_points_by_parameter.append(data_point.text)
                    parsed_data_by_station.append(data_points_by_parameter)
            parsed_data = list(zip(*parsed_data_by_station))
            all_data.append(pd.DataFrame(parsed_data, columns=column_headers))

        return pd.concat(all_data, ignore_index=True)

    def convert_wind_direction(self, parsed_data: pd.DataFrame):
        directions = self.config['wind_directions']
        for str_, val in directions.items():
            parsed_data.replace(to_replace=str_, value=val, inplace=True)

        return parsed_data

    def get_db_columns(self):
        parameters = self.config['met']['parameters']
        columns = [(parameter) for parameter in parameters.items()]
        
        return columns

    def get_db_types(self):
        parameters = self.config['met']['parameters']
        types = ''
        for parameter in parameters.values():
            types = f'{types}%{parameter}'

        return types


def main():
    # try:
    weather = Forecast()
    raw_data = weather.scrape()
    formatted_data = weather.parse(raw_data)
    finalized_data = weather.convert_wind_direction(formatted_data)
    columns = weather.get_db_columns()
    types = weather.get_db_types()
    sql = database.SQL()
    sql.write(table='weather', data=finalized_data,
              columns=columns, types=types)
    # except:
    #     logging.error(traceback.format_exc())


if __name__ == '__main__':
    fire.Fire(main)
