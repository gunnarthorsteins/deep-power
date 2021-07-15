import os
import glob
import time
import getpass
import datetime
import traceback
from pathlib import Path

# To virtually press keys when navigating the web
from selenium.webdriver.common.keys import Keys

import taskkiller
import browser
import users
import Logs
import autoupload_prop as els


IS_THIS_A_TEST = True


class AutoUpload:
    """Automatically uploads the most recent
    order to LV's and LN's portals.

    Params::
        testing (bool): If 'True' then program doesn't upload the new files
                        and runs non-headlessly (is that a word??)

    Usage:
        auto_upload = AutoUpload(testing=True)
        auto_upload.LV_upload()
        auto_upload.LN_upload()
    """

    def __init__(self, testing=True):
        self.testing = testing
        self.headless = False if testing else True
        self.user_LV, self.user_LN = self.get_user()

        now = datetime.datetime.now()
        year = now.year
        self.file_dir = f''

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        msg = traceback.format_exc(
            limit=1) if exc else 'Purch. order successful.'
        loglvl = 'CRITICAL' if exc else 'INFO'
        Logs.log(name=auto.__class__.__name__,
                 msg=msg,
                 loglvl=loglvl)

        procs = ['firefox', 'geckodriver']
        taskkiller.kill(procs)

    @staticmethod
    def get_user():
        """Checks which user is running the script.

        Returns:
            user_LV: a dict containing the LV user info:
                        username
                        pw
            user_LN: a dict containing the LN user info:
                        username
                        pw

        ToDo:
            Better password management. Currently stored as
            environment variables.
        """

        # NOTE: The passwords are omitted for security purposes
        windows_user = getpass.getuser()
        user = users.users[windows_user]
        user_LV = user['lv']
        user_LN = user['ln']

        return user_LV, user_LN

    def newest_file(self, folder):
        """Finds the most recently saved file in the desired folder.

        Params::
            folder (str): Absolute path to folder w/o a trailing slash

        Returns:
            path to most recently saved file in 'folder'
        """

        file_dir = f'{folder}/*'
        # Find all files in the current folder
        file_dir = glob.glob(file_dir)
        latest_file_LV = max(file_dir,
                             key=os.path.getctime)

        return Path(latest_file_LV)

    @staticmethod
    def LV_login(user, headless=False):
        """Logs into LV's portal.

        Returns: driver
        """

        ff = browser.LaunchFirefox(url='vidskiptavefur.lv.is',
                                   cookies=True,
                                   headless=headless)
        driver = ff()
        element = driver.find_element_by_id('userNameInput')
        element.send_keys(user['username'])
        element = driver.find_element_by_id('passwordInput')
        element.send_keys(user['pw'])
        element.send_keys(Keys.RETURN)
        # For the user to have 60s to confirm the log in on his/her phone.
        waiting = browser.Wait(driver)
        element = waiting(els.xpaths['lv_login'], 'xpath', 60)

        return driver

    def LV_upload(self):
        """Uploads the latest file to LV's portal."""

        driver = self.LV_login(self.user_LV,
                               headless=self.headless)
        driver.implicitly_wait(10)
        driver.get('https://vidskiptavefur.lv.is/orders')
        element = driver.find_element_by_xpath(els.xpaths['lv_upload'])
        element.click()
        element = driver.find_element_by_id('order-upload')

        LV_file_dir = f'{self.file_dir}Landsvirkjun'
        latest_file_LV = self.newest_file(folder=LV_file_dir)
        element.send_keys(str(latest_file_LV))
        element = driver.find_element_by_xpath(els.xpaths['lv_commit'])

        if not self.testing:
            # element.click()  # NOTE
            time.sleep(10)

        driver.quit()

    def LN_upload(self):
        """Uploads the latest file to LN's Amper portal."""

        LN_file_dir = f'{self.file_dir}Landsnet/Kaup'
        latest_file_LN = self.newest_file(folder=LN_file_dir)

        LN = browser.LaunchFirefox(url='amper.landsnet.is',
                                   cookies=True,
                                   headless=self.headless)
        driver = LN()
        element = driver.find_element_by_id('login')
        element.send_keys(self.user_LN['username'])
        element = driver.find_element_by_id('password')
        driver.implicitly_wait(10)
        element.send_keys(self.user_LN['pw'])
        element.send_keys(Keys.RETURN)
        driver.implicitly_wait(10)
        element = driver.find_element_by_link_text('Áætlanir')
        element.click()
        driver.implicitly_wait(10)
        element = driver.find_element_by_tag_name('input')
        element.send_keys(str(latest_file_LN))
        time.sleep(3)

        if not self.testing:
            element = driver.find_element_by_xpath(els.xpaths['ln_commit'])
            # element.click()  # NOTE
            time.sleep(10)

        driver.quit()


if __name__ == '__main__':
    auto_upload = AutoUpload(testing=IS_THIS_A_TEST)
    with auto_upload as auto:
        # auto.LV_upload()
        auto.LN_upload()

# Next two lines have been archived. It's not good practice to
# navigate to the most recent folder in the folder in case
# older files are also being modified.
# file_dir = max(file_dir, key=os.path.getctime)
# list_of_files = glob.glob('".join([str(file_dir),
#                           "/Landsvirkjun/*"]))
