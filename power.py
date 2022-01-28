import bs4
from bs4 import BeautifulSoup
from datetime import datetime
import json
import logging
import os
import pandas as pd

import database
from scrape import Scraper

cwd = os.getcwd() + '/'

logging.basicConfig(filename=f'{cwd}logs.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


def write_html(filename, soup):
    with open(filename, 'w') as f:
        f.write(soup.prettify())
    print('soup saved to file')


def read_html(filename):
    with open(filename) as f:
        soup = BeautifulSoup(f, 'html.parser')

    return soup


class Landsnet:
    """Scrapes from LN's XML-service.

    Logs key information on power flow on the Icelandic power grid.
    """

    def __init__(self):
        with open(f'{cwd}config.json') as f:
            self.config = json.load(f)
        self.parameters = self.config['landsnet']['parameters']

    def parse(self, soup: bs4.BeautifulSoup):
        """Converts from soup to df

        Args:
            soup (bs4.BeautifulSoup): The scraped data

        Returns:
            (pd.DataFrame): The scraped data
        """

        literal = json.loads(str(soup))
        return pd.json_normalize(literal)

    def extract_desired_values(self, parsed_data: pd.DataFrame):
        desired_keys = self.config['landsnet']['keys']
        desired_values = []
        for key in desired_keys:
            val = parsed_data[parsed_data['key'] == key]['MW'].item()
            desired_values.append(val)
        return desired_values

    def get_timestamp(self, parsed_data: pd.DataFrame):
        """Extracts the timestamp from the scraped data.

        Args:
            parsed_data (pd.DataFrame): The scraped data

        Returns:
            (str): The extracted timestamp
        """        
        return parsed_data.iloc[0, 0]

    def merge_data(self, desired_values: list, timestamp: str):
        """Merges the data to be written out to SQL

        Args:
            desired_values (list): The desired values
            timestamp (str): The timestamp

        Returns:
            (list): The data prepared for SQL
        """        
        return [timestamp] + desired_values


def main():
    with open(f'{cwd}config.json') as f:
        config = json.load(f)
    url = config['landsnet']['URL']
    with Scraper() as scrape_:
        soup = scrape_.scrape(url, 'power')
    landsnet = Landsnet()
    parsed_data = landsnet.parse(soup=soup)
    desired_values = landsnet.extract_desired_values(parsed_data)
    timestamp = landsnet.get_timestamp(parsed_data)
    final_data = landsnet.merge_data(desired_values, timestamp)
    sql = database.SQL()
    sql.write(table='landsnet', data=final_data, NO_COLUMNS=11, is_many=False)


if __name__ == "__main__":
    main()
