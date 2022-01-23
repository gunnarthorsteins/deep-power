from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class Scraper:

    def __init__(self):
        self.session = requests.Session()

    def __enter__(self):
        return self

    def _requests_retry_session(
        self,
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    ):
        """Improves scraping reliability by retrying.

        Taken from here: https://bit.ly/3Ky7LIZ

        Args:
            retries (int, optional): Number of retries. Defaults to 3.
            backoff_factor (float, optional): The amount of time to wait after a failed attempt.
                Defaults to 0.3.
            status_forcelist (tuple, optional): The exceptions to handle.
                Defaults to (500, 502, 504).

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

    def scrape(self, url: str):
        """Scrapes XML-style websites.

        Args:   
            url (str): The desired url

        Returns:
            (bs4.BeautifulSoup): The query results

        Raises:
            requests.exceptions.ConnectionError: If connection isn't made
        """

        response = self._requests_retry_session().get(url)
        if response.status_code == 200:
            return BeautifulSoup(response.content, 'html.parser')
        else:
            response.raise_for_status()

    def close(self):
        self.session.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
