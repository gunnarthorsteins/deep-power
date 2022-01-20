import os
import sys
import unittest

# To import from other parent directory in repo
pwd = os.getcwd()
sys.path.insert(0, pwd)

class TestDatabase(unittest.TestCase):
    def test_connection(self):
        pass

if __name__ == "__main__":
    unittest.main()