import os
import sys
import unittest

sys.path.append("..")

import app

class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        pass

    # executed after each test
    def tearDown(self):
        pass

###############
#### tests ####
###############

    def test_main_page(self):
        # response = self.get('/', follow_redirects=True)
        # self.assertEqual(response.status_code, 200)
        pass

if __name__ == "__main__":
    unittest.main()
