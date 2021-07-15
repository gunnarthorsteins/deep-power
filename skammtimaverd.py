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
        # with pd.ExcelWriter(dest_file,
        #                     engine='openpyxl',
        #                     datetime_format=dt_format,
        #                     mode='a') as writer:
        #     # startrow = f.sheets['Skammtimaverd'].maw_row
        #     writer.sheets = dict((ws.title, ws) for ws in writer.worksheets)
        #     self.df.to_excel(writer,
        #                      index=False,
        #                      header=False,
        #                      startrow=181,
        #                      sheet_name='Skammtimaverd')
        # TODO APPEND TO AN EXISTING SHEET, NOT A CREATE NEW ONE


if __name__ == '__main__':
    s = Skammtimaverd()
    with s as skamm:
        skamm.data_collection()
        skamm.read_xlsx()
        # skamm.write_xlsx()
        # skamm.write_csv()
        # mysql_data_manipulation()
    
    # def mysql_data_manipulation():
    #     if this_computer == "LAP-GUNNAR.hsorka.local":
    #         mydb = mysql.connector.connect(host="LAP-GUNNAR",
    #                                        user="gunnarth",
    #                                        passwd="Columbia.2020",
    #                                        database="LV_Skammtimaverd")
    #     elif this_computer == "HSOMSADFS01.hsorka.local":
    #         mydb = mysql.connector.connect(host="HSOMSADFS01",
    #                                        user="gunnarth",
    #                                        passwd="Columbia.2020",
    #                                        database="LV_Skammtimaverd")
    #     mycursor = mydb.cursor()  # Naudsynleg skipun
    #     #  mycursor.execute("TRUNCATE TABLE Skammtimaverd") 
    # # Eydir ollum gognum ur toflunni. Hafa commentad ollu jofnu

    #     # thessi blokk les inn nyjustu gognin i mySQL-toflunni og ber
    # saman vid gognin i nyjasta skjalinu
    #     # Ath ad hun virkar bara thegar gogn eru fyrir i toflunni. Fyri
    #  nyja toflu tharf ad nota blokkina fyrir nedan
    #     mycursor.execute("SELECT datetime, skammtimaverd FROM Skammtimaverd")
    #     # Nyjasta dt_str'id i toflunni (ath indexid; [-1]->Sidasta (nyjasta)
    # linan i toflunni. [0]->Fyrsta gildid (dt_str))
    #     old_dt_str = mycursor.fetchall()[-1][0]
    #     old_dt = datetime.strptime(str(old_dt_str),
    #                                r'%d.%m.%Y %H:%M')
    #     dt = []
    #     for i in range(len(dt_str)):
    #         dt = datetime.strptime(str(dt_str[i]),
    #                                r'%d.%m.%Y %H:%M')  # Breytum i-ta
    # gildinu i dt ur str i datetime svo ad vid getum borid thad saman vid
    # gognin i mySQL
    #         if dt > old_dt:
    #             dt_mySQL = dt_str[i:]
    #             skammtimaverd_mySQL = skammtimaverd[i:]

    #             #  thessi blokk skrifar gogn i LV_Skammtimaverd-tofluna
    #             sql = "INSERT INTO Skammtimaverd (Datetime,Skammtimaverd)
    # VALUES (%s,%s)"
    #             val = []
    #             for i in range(0, len(skammtimaverd_mySQL)):
    #                 val = (str(dt_mySQL[i]), str(skammtimaverd_mySQL[i]))
    #                 mycursor.execute(sql, val)
    #                 mydb.commit()  # Naudsynleg skipun - framkvaemir sjalfan
    # innslattinn
    #                 # Til ad 'skammtimaverd' se number i Excel, ekki text
    #                 mycursor.execute(
    #                     "ALTER TABLE Skammtimaverd MODIFY Skammtimaverd
    # DOUBLE")
    #                 break  # Hoppum ut ur luppunni

    #   #  thessi blokk skrifar gogn i LV_Skammtimaverd-tofluna. Bara nota 
    # hessa blokk thegar stora blokkin ad ofan er kommentud
    #  sql="INSERT INTO Skammtimaverd (Datetime,Skammtimaverd) VALUES (%s,%s)"
    #  val=[]
    #  for i in range(0,len(skammtimaverd)):
    #    val=(str(dt_str[i]),str(skammtimaverd[i]))
    #    mycursor.execute(sql,val)
    #    mydb.commit()  # Naudsynleg skipun - framkvaemir sjalfan innslattinn
    #  mycursor.execute("ALTER TABLE Skammtimaverd MODIFY Skammtimaverd
    # DOUBLE")  # Til ad 'skammtimaverd' se number i Excel, ekki text

    # AUKALiNUR FYRIR TRAKTERINGAR a MYSQL, EKKI HENDA
    #  mycursor.execute("CREATE DATABASE LV_Skammtimaverd")   # Bua til nyjan
    # gagnagrunn
    #   #  sql="DROP TABLE skammtimaverd"  # Eyda toflu
    #  mydb.commit()
    #   #  mycursor.execute("DROP TABLE skammtimaverd")  # Eydir toflunni
    #  mycursor.execute("CREATE TABLE Skammtimaverd (Datetime VARCHAR(255),
    # Skammtimaverd VARCHAR(255))")  # Bua til nyja toflu
    #  mycursor.execute("ALTER TABLE Skammtimaverd ADD COLUMN id INT
    # AUTO_INCREMENT PRIMARY KEY")  # SKYLDA: Baetir vid unique ID fyrir
    # hverja linu i toflunni

#####################################################
# Naestu skref:
# 2. Tengja mySQL vid Masterskjal
