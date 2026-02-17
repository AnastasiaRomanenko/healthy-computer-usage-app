import unittest
import time
from unittest.mock import patch
from backend.core.notification_manager import NotificationManager


class TestNotificationManager(unittest.TestCase):

    def setUp(self):
        NotificationManager._instance = None

    def test_singleton_pattern(self):
        manager1 = NotificationManager()
        manager2 = NotificationManager()

        self.assertIs(manager1, manager2)

    @patch('subprocess.run')
    def test_send_notification(self, mock_run):
        manager = NotificationManager()

        result = manager.send("Test Title", "Test Message")

        self.assertTrue(result)
        mock_run.assert_called_once()

        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "osascript")
        self.assertEqual(args[1], "-e")
        self.assertIn("Test Title", args[2])
        self.assertIn("Test Message", args[2])

    @patch('subprocess.run')
    def test_cooldown_prevents_duplicate(self, mock_run):
        manager = NotificationManager()

        result1 = manager.send("Title", "Message")
        self.assertTrue(result1)

        result2 = manager.send("Title", "Message")
        self.assertFalse(result2)

        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_cooldown_expires(self, mock_run):
        manager = NotificationManager()

        result1 = manager.send("Title", "Message")
        self.assertTrue(result1)

        time.sleep(5.1)

        result2 = manager.send("Title", "Message")
        self.assertTrue(result2)

        self.assertEqual(mock_run.call_count, 2)

    @patch('subprocess.run')
    def test_different_notifications_no_cooldown(self, mock_run):
        manager = NotificationManager()

        result1 = manager.send("Title 1", "Message 1")
        result2 = manager.send("Title 2", "Message 2")
        result3 = manager.send("Title 1", "Message 2")

        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertEqual(mock_run.call_count, 3)


class TestNotificationManagerThreadSafety(unittest.TestCase):
    def setUp(self):
        NotificationManager._instance = None

    def test_concurrent_singleton_creation(self):
        import threading

        instances = []

        def create_instance():
            manager = NotificationManager()
            instances.append(manager)

        threads = [threading.Thread(target=create_instance) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        first = instances[0]
        for instance in instances:
            self.assertIs(instance, first)


if __name__ == '__main__':
    unittest.main()
