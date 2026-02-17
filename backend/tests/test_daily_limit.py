import unittest
import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.features.daily_limit import DailyLimit
from backend.core.settings_manager import SettingsManager
from backend.core.notification_manager import NotificationManager


class TestDailyLimit(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        SettingsManager._instance = None
        NotificationManager._instance = None

        with patch('backend.features.daily_limit.SettingsManager') as mock_settings:
            self.mock_settings_instance = MagicMock()
            self.mock_settings_instance.path = self.test_dir
            self.mock_settings_instance.get.return_value = "04:00"
            mock_settings.return_value = self.mock_settings_instance

            self.daily_limit = DailyLimit()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        SettingsManager._instance = None
        NotificationManager._instance = None

    def test_create_new_usage_data(self):
        data = self.daily_limit.create_new_usage_data()

        self.assertIn('date', data)
        self.assertIn('seconds_used', data)
        self.assertIn('session_start', data)
        self.assertEqual(data['seconds_used'], 0)

        datetime.fromisoformat(data['date'])

    def test_load_usage_data_no_file(self):
        data = self.daily_limit.load_usage_data()

        self.assertEqual(data['seconds_used'], 0)
        self.assertIn('date', data)

    def test_load_usage_data_from_today(self):
        usage_data = {
            'date': datetime.now().isoformat(),
            'seconds_used': 3600,
            'session_start': datetime.now().isoformat()
        }

        with open(self.daily_limit.USAGE_DATA_FILE, 'w') as f:
            json.dump(usage_data, f)

        loaded_data = self.daily_limit.load_usage_data()

        self.assertEqual(loaded_data['seconds_used'], 3600)

    def test_load_usage_data_from_yesterday(self):
        yesterday = datetime.now() - timedelta(days=1)
        usage_data = {
            'date': yesterday.isoformat(),
            'seconds_used': 3600,
            'session_start': yesterday.isoformat()
        }

        with open(self.daily_limit.USAGE_DATA_FILE, 'w') as f:
            json.dump(usage_data, f)

        loaded_data = self.daily_limit.load_usage_data()

        self.assertEqual(loaded_data['seconds_used'], 0)

    @patch('time.sleep')
    def test_monitor_saves_usage_data(self, mock_sleep):
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        self.daily_limit.monitor()

        self.assertTrue(os.path.exists(self.daily_limit.USAGE_DATA_FILE))

        with open(self.daily_limit.USAGE_DATA_FILE, 'r') as f:
            data = json.load(f)
            self.assertIn('seconds_used', data)

    def test_usage_file_path(self):
        expected_path = os.path.join(self.test_dir, 'daily_usage.json')
        self.assertEqual(self.daily_limit.USAGE_DATA_FILE, expected_path)


if __name__ == '__main__':
    unittest.main()
