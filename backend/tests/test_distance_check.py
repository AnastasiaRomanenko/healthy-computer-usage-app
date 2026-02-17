import unittest
from unittest.mock import patch
from backend.features.distance_check import DistanceCheck


class TestDistanceCheck(unittest.TestCase):

    def setUp(self):
        self.distance_check = DistanceCheck()

    def test_distance_threshold(self):
        self.assertEqual(self.distance_check.DISTANCE_THRESHOLD, 1.2)

    def test_check_distance_healthy(self):
        from collections import deque

        healthy_area = 1000.0
        current_area = 900.0  # less than 1.2 * healthy_area

        area_history = deque([current_area], maxlen=5)
        mock_keypoints = [[290, 330, 1.0], [320, 300, 1.0], [260, 300, 1.0]]

        new_state, last_alert = self.distance_check._check_distance(
            mock_keypoints,
            healthy_area,
            area_history,
            "Healthy distance",
            0
        )

        self.assertEqual(new_state, "Healthy distance")

    @patch('subprocess.run')
    def test_check_distance_too_close(self, mock_subprocess):
        from collections import deque

        healthy_area = 1000.0
        current_area = 1300.0  # greater than 1.2 * healthy_area

        area_history = deque([current_area], maxlen=5)
        mock_keypoints = [[290, 330, 1.0], [330, 290, 1.0], [250, 290, 1.0]]

        new_state, last_alert = self.distance_check._check_distance(
            mock_keypoints,
            healthy_area,
            area_history,
            "Healthy distance",
            0
        )

        self.assertEqual(new_state, "Too close")
        self.assertEqual(mock_subprocess.call_count, 1)


if __name__ == '__main__':
    unittest.main()
