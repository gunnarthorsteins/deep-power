from datetime import datetime
import logging
import json

import database
from scrape import Scraper

logging.basicConfig(filename='logs.log',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


class Landsnet:
    """Scrapes from LN's XML-service.

    Logs key information on power flow on the Icelandic power grid.
    """

    def get_from_soup(self, val):
        return self.soup.select_one(self.config.css[val])

    def parse(self, reglun, dt, pwr):
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
    with open('config.json') as f:
        config = json.load(f)
    url = config['landsnet']['URL']
    with Scraper() as scrape_:
        soup = scrape_.scrape(url)
    with open("output1.html", "w") as f:
        f.write(str(soup))
    landsnet = Landsnet()
    # sql = database.SQL()
    # sql.write(power_data)


if __name__ == "__main__":
    main()
