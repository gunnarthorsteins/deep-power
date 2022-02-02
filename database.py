import mysql.connector
import os
import json
import logging
from mysql.connector.errors import IntegrityError


cwd = os.path.dirname(os.path.realpath(__file__))


class Setup():
    def __init__(self):
        logging.basicConfig(filename=f'{cwd}/logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

        with open(f'{cwd}/sql_config.json') as f:
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

        Args:
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

    def write(self, table: str, data: list, logging_message: str):
        '''Writes data to MySQL table.

        Args:
            table: table name
            data: data to be written out. Format is list or nested tuples
                in list if writing multiple lines
            logging_message: The filename to include in the logging message
        '''

        # Implicitly handle both single-line and multi-line inputs
        if type(data[0]) is tuple:
            NO_ENTRIES = len(data)
            NO_COLUMNS = len(data[0])
        else:
            NO_ENTRIES = 0
            NO_COLUMNS = len(data)

        # Setup
        types = str(NO_COLUMNS * f'%s,')[:-1]  # Formatting value types
        command = (f'INSERT INTO {table} VALUES ({types})')

        # Execution
        mycursor = self.mydb.cursor()  # A necessary command for every query
        try:
            if NO_ENTRIES > 1:
                mycursor.executemany(command, data)
            else:
                mycursor.execute(command, tuple(data))
            self.mydb.commit()  # A necessary command for every query
            logging.info(
                f'{logging_message}: successfully inserted to database')
        except IntegrityError:
            logging.warning(
                f'{logging_message}: SQL insertion aborted due to duplicate primary keys')

    def fetch(self, table, val):
        mycursor = self.mydb.cursor()
        mycursor.execute(f"SELECT {val} FROM {table}")
        return mycursor.fetchall()


def main():
    new_db = Create()


if __name__ == '__main__':
    sql = SQL()
    sql.fetch(table='hec_scraping', val='timestamp')
