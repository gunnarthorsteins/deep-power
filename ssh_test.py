# from sshtunnel import SSHTunnelForwarder
import requests
# import json
from bs4 import BeautifulSoup

# # server = SSHTunnelForwarder(
# #     '192.168.195.51',
# #     ssh_username="hec",
# #     ssh_password="goldman.2021",
# #     remote_bind_address=('127.0.0.1', 8080)
# # )

# # server.start()

# # print(server.local_bind_port)  # show assigned local port
# # # work with `SECRET SERVICE` through `server.local_bind_port`.


URL = 'https://amper.landsnet.is/MapData/api/measurements'
page = requests.get(URL)
soup = BeautifulSoup(page.text, 'lxml')
print(soup.prettify())

# # server.stop()

# import urllib.request

# response = urllib.request.urlopen(URL)
# text = response.read()
# print(json.loads(text.decode('utf-8')))
# import urllib3
# import json

# http = urllib3.PoolManager()
# print('start')
# r = http.request('GET', URL)
# print('finish')

# print(json.loads(r.data.decode('utf-8')))