import mysql.connector
import os
import json
import logging
from mysql.connector.errors import IntegrityError


cwd = os.path.dirname(__file__)


class Setup():
    def __init__(self):
        logging.basicConfig(filename=f'{cwd}logs.log',
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')

        f = open(f'{cwd}config.json')
        self.config = json.load(f)

        self.mydb = mysql.connector.connect(host=self.config['sql']['HOST'],
                                            user=self.config['sql']['USER'],
                                            passwd=self.config['sql']['PASSWD'],
                                            database=self.config['sql']['DATABASE'])


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

    def write(self, table: str, data: list, NO_COLUMNS: int, is_many=True):
        '''Writes data to MySQL table.

        Args:
            table: table name
            data: data to be written out. Format is list or nested tuples
                in list if writing multiple lines
            NO_COLUMNS: Number of columns in table. This is dumb but cannot
                be bothered with it for now
            is_many: Whether we're writing multiple lines. Defaults to True
        '''

        # Setup
        types = str(NO_COLUMNS * f'%s,')[:-1]  # Formatting value types
        command = (f'INSERT INTO {table} VALUES ({types})')

        # Execution
        mycursor = self.mydb.cursor()  # A necessary command for every query
        try:
            if is_many:
                mycursor.executemany(command, data)
            else:
                mycursor.execute(command, tuple(data))
            self.mydb.commit()  # A necessary command for every query
            logging.info('success: logged to database')
        except IntegrityError:
            logging.warning('sql execution aborted due to duplicate values')

    def fetch(self, table, val):
        mycursor = self.mydb.cursor()
        mycursor.execute(f"SELECT {val} FROM {table}")
        return mycursor.fetchall()


def main():
    new_db = Create()


if __name__ == '__main__':
    sql = SQL()
    sql.fetch(table='hec_scraping', val='timestamp')
