import unittest
from unittest.mock import patch
from backend.features.break_reminders import BreakReminders
from backend.core.notification_manager import NotificationManager


class TestBreakReminders(unittest.TestCase):
    def setUp(self):
        NotificationManager._instance = None
        self.break_reminders = BreakReminders()

    def test_init(self):
        self.assertIsInstance(self.break_reminders.notifier, NotificationManager)
        self.assertEqual(self.break_reminders.BREAK_INTERVAL, 20 * 60)

    @patch('time.sleep')
    def test_monitor_handles_keyboard_interrupt(self, mock_sleep):
        mock_sleep.side_effect = KeyboardInterrupt()
        try:
            self.break_reminders.monitor()
        except KeyboardInterrupt:
            self.fail("monitor() should handle KeyboardInterrupt")

    @patch('subprocess.run')
    @patch('time.sleep')
    def test_full_break_cycle(self, mock_sleep, mock_subprocess):
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        self.break_reminders.monitor()

        self.assertEqual(mock_subprocess.call_count, 1)


if __name__ == '__main__':
    unittest.main()
