import fire
from datetime import datetime
import traceback
import logging
import json

import requests
from bs4 import BeautifulSoup
from mysql.connector.errors import DatabaseError, IntegrityError, ProgrammingError

import database

logging.basicConfig(filename='logs.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


class Landsnet:
    """Scrapes current regulation value from LN's
    XML-service and saves to csv and mySQL.
    """

    def __init__(self):
        f = open('config.json')
        self.config = json.load(f)

    def get_from_soup(self, val):
        return self.soup.select_one(self.config.css[val])

    def scrape(self):
        """Scrapes LN's XML-site.

        Returns bs4.element.Tags (see BeautifulSoup documentation):
            reglun
            dt
            pwr
        """
        URL = self.config['landsnet']['URL']
        page = requests.get(URL)
        self.soup = BeautifulSoup(page.text, 'lxml')
        print(self.soup.prettify())

        # reglun = self.get_from_soup('reglun')
        # dt = self.get_from_soup('dt')
        # pwr = self.get_from_soup('pwr')
        # print(reglun, dt, pwr)

        # return reglun, dt, pwr

    def format(self, reglun, dt, pwr):
        """Intermediate data formatting before saving to database."""

        strp = r'%Y-%m-%dT%H:%M:%S'
        dt = datetime.strptime(dt.string, strp)
        strf = r'%Y-%m-%d %H:%M:%S'
        dt = dt.strftime(strf)

        reglun = '-1' if str(reglun.string) == '-1' else '1'
        reglun_bool = 'FALSE' if reglun == '-1' else 'TRUE'

        pwr = str(round(float(pwr.string)))

        power_data = {'dt': dt,
                      'reglun': reglun,
                      'bool': reglun_bool,
                      'pwr': pwr}

        return power_data


def main():
    try:
        landsnet = Landsnet()
        power_data = landsnet.scrape()
        # sql = database.SQL()
        # sql.write(power_data)

        # DatabaseError: Usually raised when SQL host is incorrect
        # ProgrammingError: SQL syntax error
        # IntegrityError: Duplicate values
    except (DatabaseError, ProgrammingError, IntegrityError):
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    fire.Fire(main)
