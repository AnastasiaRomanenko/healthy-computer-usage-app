import unittest
from backend.core.time_manager import TimeManager


class TestTimeManager(unittest.TestCase):

    def setUp(self):
        self.time_manager = TimeManager()

    def test_init(self):
        self.assertEqual(self.time_manager.CHECK_INTERVAL, 60)
        self.assertEqual(self.time_manager.WARNING_MINUTES, [120, 60, 30, 15, 5, 1])

    def test_format_time_positive_hours_and_minutes(self):
        result = self.time_manager.format_time(9000, "daily")
        self.assertEqual(result, "2 hour(s) 30 minute(s)")

    def test_format_time_only_hours(self):
        result = self.time_manager.format_time(10800, "daily")
        self.assertEqual(result, "3 hour(s)")

    def test_format_time_only_minutes(self):
        result = self.time_manager.format_time(2700, "daily")
        self.assertEqual(result, "45 minute(s)")

    def test_format_time_less_than_minute(self):
        result = self.time_manager.format_time(0, "daily")
        self.assertEqual(result, "less than 1 minute")

        result = self.time_manager.format_time(30, "daily")
        self.assertEqual(result, "less than 1 minute")

    def test_format_time_negative_daily(self):
        result = self.time_manager.format_time(-9000, "daily")
        self.assertEqual(result, "2 hour(s) 30 minute(s)")

    def test_format_time_negative_night(self):
        result = self.time_manager.format_time(-7200, "night")
        self.assertIn("hour", result)

    def test_format_time_exact_hour(self):
        result = self.time_manager.format_time(3600, "daily")
        self.assertEqual(result, "1 hour(s)")

    def test_format_time_exact_minute(self):
        result = self.time_manager.format_time(60, "daily")
        self.assertEqual(result, "1 minute(s)")

    def test_format_time_large_value(self):
        result = self.time_manager.format_time(90000, "daily")
        self.assertEqual(result, "25 hour(s)")

    def test_format_time_with_seconds_remainder(self):
        result = self.time_manager.format_time(5445, "daily")
        self.assertEqual(result, "1 hour(s) 30 minute(s)")

    def test_format_time_different_types(self):
        seconds = 3600

        daily_result = self.time_manager.format_time(seconds, "daily")
        night_result = self.time_manager.format_time(seconds, "night")
        break_result = self.time_manager.format_time(seconds, "break")

        self.assertEqual(daily_result, "1 hour(s)")
        self.assertEqual(night_result, "1 hour(s)")
        self.assertEqual(break_result, "1 hour(s)")


class TestTimeManagerEdgeCases(unittest.TestCase):
    def setUp(self):
        self.time_manager = TimeManager()

    def test_format_time_boundary_59_minutes(self):
        result = self.time_manager.format_time(3540, "daily")
        self.assertEqual(result, "59 minute(s)")

    def test_format_time_boundary_1_hour_1_second(self):
        result = self.time_manager.format_time(3601, "daily")
        self.assertEqual(result, "1 hour(s)")

    def test_format_time_zero(self):
        result = self.time_manager.format_time(0, "daily")
        self.assertEqual(result, "less than 1 minute")

    def test_format_time_negative_zero(self):
        result = self.time_manager.format_time(-0, "daily")
        self.assertEqual(result, "less than 1 minute")

    def test_format_time_max_int(self):
        result = self.time_manager.format_time(999999999, "daily")
        self.assertIsInstance(result, str)
        self.assertIn("hour", result)

    def test_check_interval_is_positive(self):
        self.assertGreater(self.time_manager.CHECK_INTERVAL, 0)

    def test_warning_minutes_all_positive(self):
        for minutes in self.time_manager.WARNING_MINUTES:
            self.assertGreater(minutes, 0)


class TestTimeManagerFormatConsistency(unittest.TestCase):

    def setUp(self):
        self.time_manager = TimeManager()

    def test_format_symmetry_positive_negative(self):
        positive = self.time_manager.format_time(7200, "daily")
        negative = self.time_manager.format_time(-7200, "daily")

        self.assertEqual(positive, negative)

    def test_format_multiple_calls_same_result(self):
        seconds = 5400

        result1 = self.time_manager.format_time(seconds, "daily")
        result2 = self.time_manager.format_time(seconds, "daily")
        result3 = self.time_manager.format_time(seconds, "daily")

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)


if __name__ == '__main__':
    unittest.main()
