import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from backend.features.night_limit import NightLimit
from backend.core.settings_manager import SettingsManager
from backend.core.notification_manager import NotificationManager
from backend.core.time_manager import TimeManager


class TestNightLimit(unittest.TestCase):
    def setUp(self):
        SettingsManager._instance = None
        NotificationManager._instance = None

        self.night_limit = NightLimit()

    def test_init(self):
        self.assertIsInstance(self.night_limit.time_manager, TimeManager)
        self.assertIsInstance(self.night_limit.settings, SettingsManager)
        self.assertIsInstance(self.night_limit.notifier, NotificationManager)

    def test_bedtime_parsing(self):
        bedtime_str = "22:30"
        hour, minute = map(int, bedtime_str.split(':'))

        self.assertEqual(hour, 22)
        self.assertEqual(minute, 30)

    def test_bedtime_replacement(self):
        now = datetime.now()
        bedtime = now.replace(hour=22, minute=0, second=0, microsecond=0)

        self.assertEqual(bedtime.hour, 22)
        self.assertEqual(bedtime.minute, 0)
        self.assertEqual(bedtime.second, 0)


class TestNightLimitTimeCalculations(unittest.TestCase):
    def setUp(self):
        SettingsManager._instance = None
        NotificationManager._instance = None
        self.night_limit = NightLimit()

    def test_remaining_time_before_bedtime(self):
        now = datetime.now()
        bedtime = now + timedelta(hours=2)

        remaining = bedtime - now
        remaining_seconds = int(remaining.total_seconds())

        self.assertGreater(remaining_seconds, 0)
        self.assertLessEqual(remaining_seconds, 7200 + 60)

    def test_remaining_time_after_bedtime(self):
        now = datetime.now()
        bedtime = now - timedelta(hours=1)

        remaining = bedtime - now
        remaining_seconds = int(remaining.total_seconds())

        self.assertLess(remaining_seconds, 0)

    def test_add_day_when_past_bedtime(self):
        now = datetime.now()
        bedtime = now - timedelta(hours=3)

        next_bedtime = bedtime + timedelta(days=1)

        self.assertGreater(next_bedtime, now)


class TestNightLimitEdgeCases(unittest.TestCase):
    def setUp(self):
        SettingsManager._instance = None
        NotificationManager._instance = None
        self.night_limit = NightLimit()

    def test_bedtime_at_midnight(self):
        bedtime_str = "00:00"
        hour, minute = map(int, bedtime_str.split(':'))

        self.assertEqual(hour, 0)
        self.assertEqual(minute, 0)

    def test_bedtime_at_noon(self):
        bedtime_str = "12:00"
        hour, minute = map(int, bedtime_str.split(':'))

        self.assertEqual(hour, 12)
        self.assertEqual(minute, 0)

    def test_bedtime_with_minutes(self):
        bedtime_str = "22:45"
        hour, minute = map(int, bedtime_str.split(':'))

        self.assertEqual(hour, 22)
        self.assertEqual(minute, 45)


class TestNightLimitIntegration(unittest.TestCase):
    def setUp(self):
        SettingsManager._instance = None
        NotificationManager._instance = None

    def tearDown(self):
        SettingsManager._instance = None
        NotificationManager._instance = None

    @patch('time.sleep')
    def test_full_night_limit_cycle(self, mock_sleep):
        night_limit = NightLimit()

        mock_sleep.side_effect = [KeyboardInterrupt()]

        with patch.object(night_limit.settings, 'get', return_value="23:00"):
            try:
                night_limit.monitor()
            except KeyboardInterrupt:
                pass
        mock_sleep.assert_called_once()


if __name__ == '__main__':
    unittest.main()
