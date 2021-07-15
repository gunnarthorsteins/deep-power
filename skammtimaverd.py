import os
import time
import glob
import socket
import openpyxl
import traceback
import pandas as pd
from pathlib import Path
from datetime import datetime

import mysql.connector

import taskkiller
from autoupload import AutoUpload as auto
import Logs


class Skammtimaverd:
    """Forrit sem saekir upplysingar um skammtimaverd
    a vefsidu LV fram i timann og vistar i gagnagrunn
    """

    def __init__(self, testing=True):
        self.testing = testing
        self.headless = False if testing else True

        self.cwd = os.getcwd()

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc:
            Logs.log(name=skamm.__class__.__name__,
                     msg=traceback.format_exc(limit=1),
                     loglvl='WARNING')
        procs = ['firefox', 'geckodriver']
        taskkiller.kill(procs)

    def data_collection(self):
        """Collects data from LV's portal."""

        user, _ = auto.get_user()
        driver = auto.LV_login(user,
                               headless=self.headless)

        url = 'https://vidskiptavefur.lv.is/shortterm'
        driver.get(url)
        xpath = '/html/body/div/div/main/div/div[1]/div[3]/div/button'
        element = driver.find_element_by_xpath(xpath)
        element.click()
        time.sleep(2)
        driver.quit()

    def read_xlsx(self):
        """Collects the desired data from the downloaded sheet."""

        downl_dir = f'{self.cwd}/Downloads/*'
        list_of_files = glob.glob(downl_dir)
        latest_lv = Path(max(list_of_files,
                             key=os.path.getctime))
        self.df = pd.read_excel(latest_lv,
                                usecols='A,D',
                                skiprows=0,
                                names=['dt',
                                       'price'])

    def write_csv(self):
        """Writes the prices to a csv."""

        self.df.to_csv('Skammtimaverd.csv',
                       mode='a',
                       header=False,
                       sep=',',
                       index=False,
                       encoding='latin1')

    def write_xlsx(self):
        """Writes the collected data to a xlsx file.

        Note:
            At the time of writing there seems to be a bug in
            numpy which raises an exception when running
            pd.to_excel(). The solution is to downgrade
            numpy to v.1.19.3 -> pip install numpy==1.19.3
        """

        self.df['dt'] = self.df['dt'].astype('datetime64[ns]')
        dest_file = f'{self.cwd}/Skammtimaverd.xlsx'
        dt_format = 'YYYY-MM-DD HH:MM'
        wb = openpyxl.load_workbook(dest_file)
        max_r = wb['Skammtimaverd'].max_row
        writer = pd.ExcelWriter(dest_file,
                                engine='openpyxl',
                                mode='a',
                                datetime_format=dt_format)
        writer.sheets = dict((ws.title, ws) for ws in wb.worksheets)
        self.df.to_excel(writer,
                         sheet_name='Skammtimaverd',
                         startrow=max_r,
                         startcol=0,
                         header=False,
                         index=False)
        writer.save()
        writer.close()
        # TODO APPEND TO AN EXISTING SHEET, NOT A CREATE NEW ONE


if __name__ == '__main__':
    s = Skammtimaverd()
    with s as skamm:
        skamm.data_collection()
        skamm.read_xlsx()
        # skamm.write_xlsx()
        # skamm.write_csv()
        # mysql_data_manipulation()