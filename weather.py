import socket
import traceback
import pandas as pd
from datetime import datetime

import mysql.connector
from bs4 import BeautifulSoup

import taskkiller
import wind
import Logs
from browser import LaunchFirefox


stations = {'Grindavík': 1361,
            'Vestmannaeyjar': 6015,
            'Hafnarfjörður': 31475,
            'Keflavík': 990}


class Forecast:
    """Scrapes meteorological data from The Met's XML-service
    and saves to a csv (for Power BI) and mySQL.

    Usage:
        weather = Forecast()
        for key, val in stations.items():
            soup = weather.scrape_data(val)
            df = weather.format_data(soup, key)
            weather.append_csv(df)
            weather.write_mySQL()

    Note:
        List of station codes is here:
        https://www.vedur.is/vedur/stodvar

        XML-service docs for additional query parameters:
        https://www.vedur.is/media/vedurstofan/XMLthjonusta.pdf
    """

    def __init__(self):
        self.t_of_run = datetime.strftime(datetime.now(),
                                          r'%Y-%m-%d %H:%M:%S')
        driver = LaunchFirefox(headless=True)
        self.driver = driver()

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc:
            Logs.log(name=weather.__class__.__name__,
                     msg=traceback.format_exc(limit=1),
                     loglvl='WARNING')
        procs = ['firefox', 'geckodriver']
        taskkiller.kill(procs)

    def scrape_data(self, station):
        """Utilizes the BeautifulSoup module for the scraping.

        Parameters:
            station (int): The station code (not the station name)
        """

        url = (f'https://xmlweather.vedur.is/?op_w=xml&'
               f'type=forec&lang=en&view=xml&ids='
               f'{str(station)}&params=F;D;T;N;R&time=1h')
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')

        return soup

    def format_data(self, soup, station):
        """Manipulates the scraped data and writes to a pandas dataframe.

        Parameters:
            soup (Beautiful Soup) from The Met's XML-service
            station (str): The station name (not the station code)
        """
        args = ['ftime', 'f', 'd', 't', 'n', 'r']
        keys = ['t_of_run', 'dt', 'station', 'wind_a',
                'wind_d', 'T', 'cl_co', 'rain']
        vals = []
        for arg in args:
            item = [i.get_text() for i in soup.find_all(arg)]
            vals.append(item)
        vals.insert(0, self.t_of_run)
        vals.insert(2, station)
        data = dict(zip(keys, vals))

        # Some additional formatting is needed for several variables
        dt_fmt = r'%Y-%m-%d %H:%M:%S'
        data['dt'] = [datetime.strptime(i, dt_fmt) for i in data['dt']]
        data['T'] = [int(i) for i in data['T']]
        data['cl_co'] = [round(0.01*int(i), 2) for i in data['cl_co']]
        # Agaleg lúppa, en næ ekki að stilla upp list comprehension f me sideways
        wind_d = []
        for item in data['wind_d']:
            for key, val in wind.wind.items():
                if item == key:
                    wind_d.append(val)
                    break
        data['wind_d'] = wind_d

        return pd.DataFrame(data)

    def append_csv(self, df):
        """Writes the meteorological data to a csv.

        Parameters:
            df (pd.dataframe)

        Note:
            encoding='latin1' is for accent letters
        """

        df.to_csv('weather.csv',
                  mode='a',
                  header=False,
                  sep='\t',
                  index=False,
                  encoding='latin1')

    def write_mySQL(self, station):
        this_computer = socket.getfqdn()

        assert this_computer == 'HSOMSADFS01.hsorka.local'
        mydb = mysql.connector.connect(host='HSOMSADFS01',
                                       user='gunnarth',
                                       passwd='Columbia.2020',
                                       database='LV_Skammtimaverd')
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


if __name__ == '__main__':
    w = Forecast()
    with w as weather:
        for key, val in stations.items():
            soup = weather.scrape_data(val)
            df = weather.format_data(soup, key)
            weather.append_csv(df)
            # weather.write_mySQL()


# # Extra lines for MySQL, do not remove
# Create a new databaste
# # mycursor.execute('CREATE DATABASE LV_Skammtimaverd')
# # # sql='DROP TABLE skammtimaverd' #Eyda toflu
# # mydb.commit()
# Removes all data from table
# # mycursor.execute('TRUNCATE TABLE Skammtimaverd')
# Deletes table
# # mycursor.execute('DROP TABLE Weather_Data')
# Create a new table
# # mycursor.execute('CREATE TABLE Weather_Data
#           (DT_Run_Time VARCHAR(255), Datetime VARCHAR(255),
#           Station VARCHAR(255), wind_a VARCHAR(255),
#           wind_d VARCHAR(255), Temperature VARCHAR(255)
#            Cloud_Cover VARCHAR(255), Rain VARCHAR(255))')
 #Necessary: Adds a unique ID for every line in table
# # mycursor.execute('ALTER TABLE Weather_Data ADD COLUMN id INT
#                   AUTO_INCREMENT PRIMARY KEY')