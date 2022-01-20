import json
import requests
import logging
import pandas as pd
import traceback
from datetime import datetime
from bs4 import BeautifulSoup

import database


class Forecast:
    """Scrapes meteorological data from The Met's XML-service,
    formats, and finally saves to a sql database.

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
            if r.status_code == 200:
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
        nonrelational_data = dict()
        # all_forecasts = pd.DataFrame(columns=parameters.keys())
        for station_names, data_by_station in raw_data.items():
            print(pd.read_xml(data_by_station))
            # nonrelational_data[station_names] =
            # for parameter in parameters.values():
            #     for tag in data_by_station.find_all(parameter):
            #         # nonrelational_data[]
            #         # sequence = data.find_all(feature)
            #         # print(tag.string)
            #         pass
            break
        # vals = []
        # for arg in args:
        #     item = [i.get_text() for i in soup.find_all(arg)]
        #     vals.append(item)
        # vals.insert(0, self.t_of_run)
        # vals.insert(2, station)
        # data = dict(zip(keys, vals))

        # # Some additional formatting is needed for several variables
        # dt_fmt = r'%Y-%m-%d %H:%M:%S'
        # data['dt'] = [datetime.strptime(i, dt_fmt) for i in data['dt']]
        # data['T'] = [int(i) for i in data['T']]
        # data['cl_co'] = [round(0.01*int(i), 2) for i in data['cl_co']]
        # # Agaleg lúppa, en næ ekki að stilla upp list comprehension f me sideways
        # wind_d = []
        # for item in data['wind_d']:
        #     for key, val in wind.wind.items():
        #         if item == key:
        #             wind_d.append(val)
        #             break
        # data['wind_d'] = wind_d

        # return pd.DataFrame(data)

    def write(self, station):
        """[summary]

        Args:
            station ([type]): [description]
        """

        mycursor = mydb.cursor()  # Naudsynleg skipun

        # Skrifum gogn i Weather_Data-tofluna
        sql = ('INSERT INTO Weather_Data (DT_Run_Time,Datetime,Station,'
               'wind_a,wind_d,Temperature,Cloud_Cover,Rain)'
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)')
        val = []
        for j in range(len(self.dt)):
            val = (self.t,
                   self.dt[j],
                   station,
                   self.wind_a[j],
                   self.wind_d[j],
                   self.T[j],
                   self.cloud_cover[j],
                   self.rain[j])
            mycursor.execute(sql, val)
            mydb.commit()  # Nauðsynleg skipun - framkvæmir sjálfan innsláttinn


def main():
    try:
        weather = Forecast()
        raw_data = weather.scrape()
        formatted_data = weather.parse(raw_data)
    except:
        logging.error(traceback.format_exc())


if __name__ == '__main__':
    main()
