import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.features.blue_light_filter import BlueLightFilter
from backend.core.settings_manager import SettingsManager
from backend.core.notification_manager import NotificationManager


class TestBlueLightFilter(unittest.TestCase):
    def setUp(self):
        SettingsManager._instance = None
        NotificationManager._instance = None

        self.blue_light = BlueLightFilter()

    def test_init(self):
        self.assertIsInstance(self.blue_light.settings, SettingsManager)
        self.assertIsInstance(self.blue_light.notifier, NotificationManager)
        self.assertIsNone(self.blue_light.current_period)
        self.assertIsNone(self.blue_light.last_notification_period)

    def test_constants(self):
        self.assertEqual(self.blue_light.DAY_START, 6)
        self.assertEqual(self.blue_light.EVENING_START, 18)
        self.assertEqual(self.blue_light.NIGHT_START, 21)
        self.assertEqual(self.blue_light.CHECK_INTERVAL, 60)

    def test_get_current_period_day(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 12, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "day")

    def test_get_current_period_evening(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 19, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "evening")

    def test_get_current_period_night(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 22, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "night")

    def test_get_current_period_early_morning(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 3, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "night")

    def test_get_current_period_boundary_day_evening(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 18, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "evening")

    def test_get_current_period_boundary_evening_night(self):
        with patch('backend.features.blue_light_filter.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2026, 1, 1, 21, 0)

            period = self.blue_light.get_current_period()
            self.assertEqual(period, "night")

    @patch('subprocess.run')
    def test_apply_filter_checks_nightlight(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        self.blue_light.apply_filter("day", 20)

        mock_run.assert_called()

    @patch('subprocess.run')
    def test_apply_filter_installs_nightlight_if_missing(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=1),  # nightlight not found
            MagicMock(returncode=0)  # brew install success
        ]

        self.blue_light.apply_filter("day", 20)

        calls = mock_run.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertIn("brew", calls[1][0][0])

    @patch('subprocess.run')
    def test_apply_filter_enables_nightlight(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=0),
            MagicMock(returncode=0),  # nightlight found
            MagicMock(returncode=0),  # nightlight on
            MagicMock(returncode=0)  # nightlight temp
        ]

        self.blue_light.apply_filter("evening", 50)

        calls = [call[0][0] for call in mock_run.call_args_list]
        self.assertIn(["nightlight", "on"], calls)
        self.assertIn(["nightlight", "temp", "50"], calls)

    def test_get_setting_for_day(self):
        with patch.object(self.blue_light.settings, 'get', return_value=20):
            value = self.blue_light.settings.get("blue_light_filter_day", 0)

            self.assertEqual(value, 20)

    def test_get_setting_for_evening(self):
        with patch.object(self.blue_light.settings, 'get', return_value=50):
            value = self.blue_light.settings.get("blue_light_filter_evening", 0)

            self.assertEqual(value, 50)

    def test_get_setting_for_night(self):
        with patch.object(self.blue_light.settings, 'get', return_value=80):
            value = self.blue_light.settings.get("blue_light_filter_night", 0)

            self.assertEqual(value, 80)


if __name__ == '__main__':
    unittest.main()
