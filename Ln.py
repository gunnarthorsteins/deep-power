import requests
from datetime import datetime
import traceback
import pandas as pd

# import mysql.connector
from bs4 import BeautifulSoup

import Logs
import Ln_prop
import taskkiller


class Landsnet:
    """Scrapes current regulation value from LN's
    XML-service and saves to csv and mySQL.
    """

    def __init__(self, headless=True):
        self.headless = headless
        self.file = 'Ln.csv'

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc:
            Logs.log(name=LN.__class__.__name__,
                     msg=traceback.format_exc(limit=1),
                     loglvl='WARNING')

    def data_collection(self):
        """Scrapes LN's XML-site.

        Returns bs4.element.Tags (see BeautifulSoup documentation):
            reglun
            dt
            pwr
        """


        url = 'https://amper.landsnet.is/MapData/api/measurements'
        page = requests.get(url)
        soup = BeautifulSoup(page.text,
                             'lxml')

        reglun = soup.select_one(Ln_prop.css['reglun'])
        dt = soup.select_one(Ln_prop.css['dt'])
        pwr = soup.select_one(Ln_prop.css['pwr'])
        print(reglun, dt, pwr)

        return reglun, dt, pwr

    def data_formatting(self, reglun, dt, pwr):
        """Formats the data nicely before writing out."""

        strp = r'%Y-%m-%dT%H:%M:%S'
        dt = datetime.strptime(dt.string, strp)
        strf = r'%Y-%m-%d %H:%M'
        dt = dt.strftime(strf)

        reglun = '-1' if str(reglun.string) == '-1' else '1'
        reglun_bool = 'FALSE' if reglun == '-1' else 'TRUE'

        pwr = str(round(float(pwr.string)))

        data = {'dt': dt,
                'reglun': reglun,
                'bool': reglun_bool,
                'pwr': pwr}
        self.df = pd.DataFrame(data=data,
                               index=[0])

    def dt_comparison(self):
        """Determines whether the current timestamp
        matches the latest logged timestamp.

        Paramaters:
            dt (np.ndarray): A timestamp

        Returns:
            A boolean expressing whether the latest
            and the current timestamp are NOT identical.
        """

        df_file = pd.read_csv(self.file,
                              sep='\t')
        last_value = df_file.tail(1)['D&T'].to_numpy()

        return last_value != self.df.dt.to_numpy()

    def append_csv(self):
        """Writes the LN data to a csv file."""

        self.df.to_csv(self.file,
                       mode='a',
                       header=False,
                       sep='\t',
                       index=False,
                       encoding='latin1')
   

    def write_mysql(self):
        """Writes the LN data to a mySQL table."""
        mydb = mysql.connector.connect(host="",
                                       user="",
                                       passwd="",
                                       database="")
        mycursor = mydb.cursor()  # A necessary command
        sql = ('INSERT INTO Aflflutningur '
               '(Datetime,Reglun,Heildarflutningur) '
               'VALUES (%s,%s,%s)')
        val = (str(self.dt),
               str(self.reglun),
               str(self.pwr))
        mycursor.execute(sql, val)
        mydb.commit()  # A necessary command


if __name__ == "__main__":
    landsnet = Landsnet()
    with landsnet as LN:
        reglun, dt, pwr = LN.data_collection()
        LN.data_formatting(reglun, dt, pwr)
        bool_val = LN.dt_comparison()
        if bool_val:
            LN.append_csv()
            
            # LN.write_mysql()
        else:
            Logs.log(name=LN.__class__.__name__,
                     msg='Latest matches current',
                     loglvl='INFO')
