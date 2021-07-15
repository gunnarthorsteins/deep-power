"""For launching an instance of a browser for automatic navigation."""

import os
import glob
import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# To run browsers headlessly
from selenium.webdriver.chrome.options import Options as chr_options
from selenium.webdriver.firefox.options import Options as ff_options


class Browser:
    """Backend for subclasses LaunchFirefox and LaunchChrome."""

    def __init__(self, url, options,
                 headless=False, cookies=False):
        https_finder = url.find('https://')
        self.url = f'https://{url}' if https_finder else url

        self.headless = headless
        self.cookies = cookies
        self.options = options
        self.options.headless = self.headless

        self.user = getpass.getuser()

    def set_properties(self, driver, headless=False):
        """"Sets miscallenous properties for the browser."""

        if not headless:
            driver.maximize_window()

        driver.get(self.url)
        driver.implicitly_wait(20)

        return driver


class LaunchFirefox(Browser):
    """Launches an instance of Firefox.

    Parameters:
        url (str): The url which is to navigated to,
                   either w. or w/o 'https://'
        headless (bool): Boolean expressing whether browser should be
                         run headlessly - i.e. in the background - or not.
        cookies (bool): Boolean expressing whether browser should be run with
                        cookies or not

    Usage:
        import browser
        driver = browser.LaunchFirefox(url='hsorka.is',
                                       headless=True,
                                       cookies=True)
        driver = driver()
    """

    def __init__(self, url='hsorka.is', headless=False, cookies=False):
        self.options = ff_options()
        super().__init__(url=url,
                         options=self.options,
                         headless=headless,
                         cookies=cookies)

    def __call__(self):
        ff_dir = (f'C:/Users/{self.user}'
                  f'/AppData/Roaming/Mozilla/Firefox/Profiles/*')
        ff_cookies = glob.glob(ff_dir)[0] if self.cookies else None

        ff_profile = webdriver.FirefoxProfile(ff_cookies)
        # commands = {'browser.download.folderList': 2,
        #             'browser.download.dir': f'{os.getcwd()}/Downloads'}
        # for key, val in commands.items():
        #     ff_profile.set_preference(key, val)

        self.driver = webdriver.Firefox(options=self.options,
                                        firefox_profile=ff_profile,
                                        service_log_path='nul')
        self.driver = self.set_properties(self.driver, self.options.headless)

        return self.driver


class LaunchChrome(Browser):
    """Launches an instance of Firefox.

    Parameters:
        url (str): The url which is to navigated to
                   either w. or w/o 'https://'
        headless (bool): Boolean expressing whether browser should be
                         run headlessly -i.e. in the background- or not.

    Usage:
        import browser
        driver = browser.LaunchChrome(url='hsorka.is',
                                      headless=True)
        driver = driver()

    Note:
        Selenium doesn't have the option of running Chrome with cookies.
        However this is possible in Firefox which usually makes it
        the weapon of choice.
    """

    def __init__(self, url, headless=False):
        self.cwd = os.getcwd()
        self.options = chr_options()
        # Set the download directory
        prefs = {'download.default_directory': f'{self.cwd}\\Downloads'}
        self.options.add_experimental_option('prefs', prefs)
        super().__init__(url=url,
                         options=self.options,
                         headless=headless,
                         cookies=False)

    def __call__(self):
        self.driver = webdriver.Chrome(f'{self.cwd}/Drivers/chromedriver.exe',
                                       options=self.options)
        self.driver = self.set_properties(self.driver, self.options.headless)

        return self.driver


class Wait:
    """Pauses until the next element which is to be interacted with is
    available. Especially useful when logging on. Is way faster and
    more robust than using time.sleep(x)

    Parameters:
        locator (str): The locator of the the next element
                       the navigator will be interacting with.
        el_type (str): The element type, e.g. xpath or id.
                       See selenium's 'By' documentation for all type options.
        time (int): Default 60. The maximum amount of waiting in
                    seconds before terminating the process.

    Returns:
        element: The actual element which can then be interacted with.

    Example:
        waiting = browser.Wait(driver)
        element = waiting(xpath, 'xpath', 60)

    Note:
        Only works for visible elements.

    ToDo:
        Make work with invisible elements.
    """

    def __init__(self, driver):
        self.driver = driver

    def __call__(self, locator, el_type, time=60):
        el_type = el_type.lower()
        el_pres = EC.presence_of_element_located((el_type,
                                                  locator))
        WebDriverWait(self.driver, time).until(el_pres)
        if el_type == 'xpath':
            element = self.driver.find_element_by_xpath(locator)
        elif el_type == 'id':
            element = self.driver.find_element_by_id(locator)
        else:
            print('This type of element hasn\'t been set up yet '
                  'since the lazy bastard who wrote it didn\'t think'
                  'it\'d be necessary')

        return element


# For testing
if __name__ == '__main__':
    driver = LaunchChrome(url='hsorka.is',
                          headless=False)
    driver = driver()
