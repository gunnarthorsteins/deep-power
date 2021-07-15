import datetime
import os
import csv
import glob
import time
import getpass
import traceback
import numpy as np
import pandas as pd
import datetime

# To virtually press keyboard keys
from selenium.webdriver.common.keys import Keys

import Logs
import browser
import taskkiller


SVA_COL = 26860
REY_COL = 26861
ROW = 15024
DASHBOARD_NO = 87


class UpdateVista:
    """Scrapes HS Orka's net production from Vista Data Vision and saves in
    a csv to display in the power market PBI report in near real-time.
    """

    def __init__(self):
        self.user_vista = os.environ.get('vista_user')
        self.pw_vista = os.environ.get('vista_pw')

        self.user = getpass.getuser()
        self.cwd = os.getcwd()
        self.url = 'https://gogn.vista.is'

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc:
            msg = traceback.format_exc(limit=1)
            loglvl = 'WARNING'
        else:
            msg = 'Latest matches current'
            loglvl = 'INFO'
        Logs.log(name=vista.__class__.__name__,
                 msg=msg,
                 loglvl=loglvl)

        procs = ['chromedriver']
        taskkiller.kill(procs)

    def vista_login(self):
        """Logs on to Vista's data portal.

        ToDo:
            Don't store the password as an environment variable.
        """

        driver = browser.LaunchChrome(url=self.url,
                                      headless=False)
        self.driver = driver()
        # Would probably be simpler and safer to launch the browser
        # with cookies and thus skipping the following log-in process
        # but this needs to be run on Chrome and unfortunately it
        # doesn't have the option of running with cookies.
        els = {'f_user': self.user_vista,
               'f_pass': self.pw_vista,
               'f_login': Keys.RETURN}
        for key, val in els.items():
            element = self.driver.find_element_by_id(key)
            element.send_keys(val)
        time.sleep(3)

    def download_data(self, dashboard_no, col, row):
        """Scrapes data from Vista's data portal dashboards.

        Parameters:
            dashboard_no (int): The dashboard number from where data
                                will be scraped. Is at the end of the url.
            col (int): The column reference in the dashboard's source code.
            row (int): The row reference in the dashboard's source code.

        Raises:
            javascript error: Cannot read property 'click' of null
                        This happens occasionally as Vista (quite annoyingly)
                        changes the source code.
        """

        url = f'{self.url}/vdv.php/dashboard/{str(dashboard_no)}'
        self.driver.get(url)

        id_frame = 'IDContentFrame'
        waiting = browser.Wait(self.driver)
        element = waiting(id_frame, 'id')
        self.driver.switch_to.frame(element)
        time.sleep(2)
        js = (f"javascript:document.getElementById('"
              f"downloadCol{str(col)}Row{str(row)}').click();")
        self.driver.execute_script(js)
        time.sleep(3)

    def format_data(self, delim='\t', skiprows=5):
        """Formats data downloaded from Vista's data portal.

        Parameters:
            delim (str): Somehow the txt files downloaded from Vista
                         have varying delimiters, either one or two tabs.
            skiprows (int): The number of rows to be skipped bc the Vista
                            files contain a fixed length docstring at the
                            top of file.

        Returns:
            dt (np.datetime): The latest timestamp in the
                              file downloaded from Vista.
            pwr (int): The power value associated with the timestamp
        """

        download_folder = f'{self.cwd}/Downloads/*'
        list_of_files = glob.glob(download_folder)
        list_of_files.sort(key=os.path.getctime)
        latest_file = list_of_files[len(list_of_files)-1]

        # engine='python' is to suppress a warning raised by decimal=','
        df = pd.read_csv(latest_file,
                         skiprows=skiprows,
                         names=['dt', 'power'],
                         sep=delim,
                         decimal=',',
                         engine='python')
        df.dt = pd.to_datetime(df.dt)
        dt = df.dt.values[-1]
        pwr = df.power.iloc[[-1]].to_numpy()

        # os.remove(latest_file)

        return dt, pwr

    def dt_comparison(self, latest):
        """Determines whether the current timestamp matches the latest logged
        timestamp.

        Parameters:
            latest (np.ndarray): A timestamp

        Returns:
            A boolean stating whether the current timestamp
            does NOT match the latest logged timestamp.
        """
        df = pd.read_csv(f'{self.cwd}/vista.csv',
                         sep='\t',
                         decimal=',',
                         engine='python')
        df.Datetime = pd.to_datetime(df.Datetime)
        dt = df.Datetime.values[-1]
        print(dt)
        print(latest)
        bool_val = dt != latest

        return bool_val

    def write_csv(self, dt, pwr_sva, pwr_rey):
        """Writes the timestamp and the power values to a textfile.

        Parameters:
            dt()
        """
        with open(f'{self.cwd}/vista.csv',
                  mode='a') as f:
            write = csv.writer(f,
                               delimiter="\t",
                               lineterminator="\n")
            write.writerow([dt,
                            pwr_sva,
                            pwr_rey])


if __name__ == '__main__':
    v = UpdateVista()
    with v as vista:
        # vista.vista_login()
        # vista.download_data(DASHBOARD_NO,
        #                     SVA_COL,
        #                     ROW)
        dt, pwr_sva = vista.format_data()
        bool_val = vista.dt_comparison(dt)
        if bool_val:
            # vista.download_data(DASHBOARD_NO,
            #                     REY_COL,
            #                     ROW)
            _, pwr_rey = vista.format_data()
            # dt = datetime.datetime.fromisoformat(str(dt)[:19])
            # strf = r'%Y-%m-%d %H:%M'
            # dt = dt.strftime(strf)
            # print(dt)

            vista.write_csv(dt=dt,
                            pwr_sva=pwr_sva,
                            pwr_rey=pwr_rey)
