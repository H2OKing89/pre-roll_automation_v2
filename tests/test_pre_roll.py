# tests/test_pre_roll.py

import unittest
from unittest.mock import patch, MagicMock
from app.utils import select_pre_roll, get_current_holiday, update_plex_pre_roll
from app.config import Config

class TestPreRoll(unittest.TestCase):
    def setUp(self):
        """
        Set up mock configurations before each test.
        """
        # Mock configuration data
        self.original_holidays = Config.HOLIDAYS
        self.original_schedule = Config.SCHEDULE
        self.original_base_pre_roll_dir = Config.BASE_PRE_ROLL_DIR

        Config.HOLIDAYS = [
            {
                "name": "Test Holiday",
                "start_date": "01-01",
                "end_date": "01-02",
                "pre_rolls": [
                    "test/holiday1.mp4",
                    "test/holiday2.mp4"
                ],
                "selection_mode": "sequential",
                "last_index": 0
            }
        ]
        Config.SCHEDULE = {
            "tasks": [
                {"name": "Test Task", "time": "00:00"}
            ]
        }
        Config.BASE_PRE_ROLL_DIR = "/pre-rolls/plex"

    def tearDown(self):
        """
        Restore original configurations after each test.
        """
        Config.HOLIDAYS = self.original_holidays
        Config.SCHEDULE = self.original_schedule
        Config.BASE_PRE_ROLL_DIR = self.original_base_pre_roll_dir

    def test_select_pre_roll_random(self):
        """
        Test selecting a pre-roll video in random mode.
        """
        with patch('random.choice', return_value="test/holiday1.mp4"):
            holiday = Config.HOLIDAYS[0]
            holiday['selection_mode'] = 'random'
            selected = select_pre_roll(holiday)
            self.assertEqual(selected, "/pre-rolls/plex/test/holiday1.mp4")

    def test_select_pre_roll_sequential(self):
        """
        Test selecting pre-roll videos in sequential mode.
        """
        holiday = Config.HOLIDAYS[0]
        holiday['selection_mode'] = 'sequential'

        # First selection
        selected1 = select_pre_roll(holiday)
        self.assertEqual(selected1, "/pre-rolls/plex/test/holiday1.mp4")
        self.assertEqual(holiday['last_index'], 1)

        # Second selection
        selected2 = select_pre_roll(holiday)
        self.assertEqual(selected2, "/pre-rolls/plex/test/holiday2.mp4")
        self.assertEqual(holiday['last_index'], 0)

    def test_select_pre_roll_no_pre_rolls(self):
        """
        Test behavior when no pre-rolls are available.
        """
        holiday = {
            "name": "Empty Holiday",
            "start_date": "02-01",
            "end_date": "02-02",
            "pre_rolls": [],
            "selection_mode": "random",
            "last_index": 0
        }
        selected = select_pre_roll(holiday)
        self.assertIsNone(selected)

    @patch('app.utils.PlexServer')
    def test_update_plex_pre_roll_success(self, mock_plex_server):
        """
        Test successful update of Plex pre-roll.
        """
        mock_instance = MagicMock()
        mock_plex_server.return_value = mock_instance

        pre_roll_path = "/pre-rolls/plex/test/holiday1.mp4"
        update_plex_pre_roll(pre_roll_path)

        # Verify PlexServer was initialized with correct parameters
        mock_plex_server.assert_called_with(Config.PLEX_HOST, Config.PLEX_TOKEN)
        # Verify that settings were attempted to be updated
        # Note: Adjust based on actual Plex API methods
        self.assertTrue(mock_instance.settings.get.called)

    @patch('app.utils.PlexServer')
    def test_update_plex_pre_roll_failure(self, mock_plex_server):
        """
        Test handling of Plex pre-roll update failure.
        """
        mock_plex_server.side_effect = Exception("Plex server connection failed.")

        pre_roll_path = "/pre-rolls/plex/test/holiday1.mp4"
        with self.assertLogs(level='ERROR') as log:
            update_plex_pre_roll(pre_roll_path)
            self.assertIn("Failed to update Plex pre-roll: Plex server connection failed.", log.output[0])

    @patch('app.utils.datetime')
    def test_get_current_holiday_within_holiday(self, mock_datetime):
        """
        Test determining the current holiday when within a holiday period.
        """
        # Mock current date to be within the Test Holiday period
        mock_now = datetime(2024, 1, 1, tzinfo=pytz.timezone(Config.TIMEZONE))
        mock_datetime.now.return_value = mock_now

        holiday = get_current_holiday()
        self.assertIsNotNone(holiday)
        self.assertEqual(holiday['name'], "Test Holiday")

    @patch('app.utils.datetime')
    def test_get_current_holiday_outside_holiday(self, mock_datetime):
        """
        Test determining the current holiday when not within any holiday period.
        """
        # Mock current date to be outside any holiday period
        mock_now = datetime(2024, 2, 1, tzinfo=pytz.timezone(Config.TIMEZONE))
        mock_datetime.now.return_value = mock_now

        holiday = get_current_holiday()
        self.assertIsNone(holiday)

if __name__ == '__main__':
    unittest.main()
