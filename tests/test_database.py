import os
import sys
import unittest

# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)

from database import SQL

class TestDatabase(unittest.TestCase):
    def test_instance(self):
        sql = SQL()
        self.assertIsInstance(sql, SQL)        

if __name__ == "__main__":
    unittest.main()