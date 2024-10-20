# tests/test_pre_roll.py

import unittest
from app.utils import perform_pre_roll

class TestPreRoll(unittest.TestCase):
    def test_perform_pre_roll(self):
        result = perform_pre_roll()
        self.assertEqual(result, "Pre-roll completed successfully.")

if __name__ == '__main__':
    unittest.main()
