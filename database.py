import mysql.connector
import os
import json
import logging
from mysql.connector.errors import Error

directory = os.path.dirname(__file__)


class Setup():
    def __init__(self):
        logging.basicConfig(filename='logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

        f = open('config.json')
        self.config = json.load(f)

        self.mydb = mysql.connector.connect(host=self.config['HOST'],
                                            user=self.config['USER'],
                                            passwd=self.config['PASSWD'],
                                            database=self.config['DATABASE'])


class Create(Setup):
    """Sets up the SQL schema.
    Am not including a db-generator because I prefer doing it in terminal.
    """

    def __init__(self):
        super().__init__()

    def create_table(self, name: str, command: tuple):
        """Creates a table in MySQL database

        Params:
            name: table name
            command: Cannot be bothered making more lower level.
                     Should be of format (name VARCHAR(50), has_a_big_head BINARY)
        """

        mycursor = self.mydb.cursor()
        mycursor.execute(f'CREATE TABLE {name} {command}')
        logging.info(f'Table {name} created')


class SQL(Setup):
    """Contains all necessary CRUD methods to interact with MySQL database"""

    def __init__(self):
        super().__init__()
        if not self.mydb.is_connected():  # Checking whether connection was successful
            logging.error('Unsuccessful in connecting to database')
            raise Error

    def write(self, table: str, data: list):
        '''Writes data to MySQL table.
        Params:
            table: table name
            data: data to be written out. Format within list shouldn't matter
        '''

        # Setup
        columns = ','.join(self.config['columns'])  # Formatting column names
        types = str(len(self.config['columns']) *
                    f'%s,')[:-1]  # Formatting value types
        command = (f'INSERT INTO {table} ({columns}) VALUES ({types})')

        # Execution
        mycursor = self.mydb.cursor()  # A necessary command for every query
        mycursor.execute(command, tuple(data))
        self.mydb.commit()
        logging.info('Success: Logged to database')

    def fetch(self, table, val):
        mycursor = self.mydb.cursor()
        mycursor.execute(f"SELECT {val} FROM {table}")
        return mycursor.fetchall()


def main():
    new_db = Create()


if __name__ == '__main__':
    sql = SQL()
    sql.fetch(table='hec_scraping', val='timestamp')
