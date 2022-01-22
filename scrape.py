import requests
from bs4 import BeautifulSoup

def scrape(url: str):
    """Scrapes weather forecasts from Icelandic Met.

    Stations and parameters configured in config.json.

    Args:
        station_id (str): The station ID (see class description)

    Returns:
        (bs4.BeautifulSoup): The query results

    Raises:
        requests.exceptions.ConnectionError: If connection isn't made
    """

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        # TODO: Raise different requests exception
        raise requests.exceptions.ConnectionError

    return BeautifulSoup(r.content, 'html.parser')
