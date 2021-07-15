import time
import traceback

import browser
import Logs
import pbi_prop
import taskkiller


class PBIUpdate:
    """Manually updates the Power Bi report.
    It's definitely not written in a general manner, the url and the
    css selector need to be adjusted for the desired report.

    Note:
        Requires that the Office365 user and password are saved in Firefox,
        which is in compliance with safety standards and eliminates the
        need for storing the password somewhere locally in plain text.
        The saved password obviously needs to be updated manually when the
        Office password is updated.
    """

    def __init__(self, headless=True):
        self.headless = headless

    def __enter__(self):
        return self

    def __exit__(self, exc, exc_val, exc_tb):
        if exc:
            Logs.log(name=pbi.__class__.__name__,
                     msg=traceback.format_exc(limit=1),
                     loglvl='WARNING')
        procs = ['firefox', 'geckodriver']
        taskkiller.kill(procs)

    def update(self):
        driver = browser.LaunchFirefox(url=pbi_prop.url,
                                       cookies=True,
                                       headless=self.headless)
        driver = driver()
        element = driver.find_element_by_css_selector(pbi_prop.css)
        element.click()
        time.sleep(5)


if __name__ == "__main__":
    pbi = PBIUpdate()
    with pbi as pbi:
        pbi.update()
