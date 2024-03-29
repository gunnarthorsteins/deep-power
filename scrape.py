from bs4 import BeautifulSoup
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import traceback


class Scraper:

    def __init__(self):
        self.session = requests.Session()
        logging.basicConfig(filename='logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

    def __enter__(self):
        return self

    def _requests_retry_session(
        self,
        retries=10,
        backoff_factor=0.5,
        status_forcelist=(500, 502, 504, 522),
    ):
        """Improves scraping reliability by retrying.

        Adapted from: https://bit.ly/3Ky7LIZ

        Args:
            retries (int, optional): Number of retries. Defaults to 10.
            backoff_factor (float, optional): The amount of time to wait after a failed attempt.
                Defaults to 0.5.
            status_forcelist (tuple, optional): The Error Codes to retry after failing on.
                Note: Landsnet typically fails on 522.

        Returns:
            (requests.sessions.Session): The requests session
        """
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)

        return self.session

    def scrape(self, url: str, description: str):
        """Scrapes XML-style websites.

        Args:   
            url (str): The desired url
            description (str): The file for writing out logs

        Returns:
            (bs4.BeautifulSoup): The query results

        Raises:
            requests.exceptions.ConnectionError: If connection isn't made
        """

        response = self._requests_retry_session().get(url, timeout=5)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            logging.warning(f'{description}: scraping failed')
            response.raise_for_status()

    def close(self):
        """Ensures session is closed, incl. when an exception is raised."""
        self.session.close()

    def __exit__(self, _, exc_value, traceback):
        self.close()
