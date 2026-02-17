import unittest
from unittest.mock import patch

from backend.features.eye_strain_prevention import EyeStrainPrevention


class TestDistanceCheck(unittest.TestCase):

    def setUp(self):
        self.eye_strain_prevention = EyeStrainPrevention()

    def test_eye_strain_threshold(self):
        self.assertEqual(self.eye_strain_prevention.TENSION_THRESHOLD, 1.2)

    @patch('subprocess.run')
    def test_check_eye_strain(self, mock_subprocess):
        from collections import deque

        relaxed_ratios = [1.8, 1.8]

        ratio_history = [deque([2.1], maxlen=5), deque([2.1], maxlen=5)]

        boxes = [[240, 285, 280, 300], [320, 285, 360, 300]]
        new_state, last_alert = self.eye_strain_prevention._check_tension(
            boxes,
            relaxed_ratios,
            ratio_history,
            "Relaxed face",
            0
        )

        self.assertEqual(new_state, "Focused face")
        self.assertEqual(mock_subprocess.call_count, 1)

    def test_check_no_eye_strain(self):
        from collections import deque

        relaxed_ratios = [1.8, 1.8]

        ratio_history = [deque([1.8], maxlen=5), deque([1.8], maxlen=5)]

        boxes = [[240, 275, 280, 305], [320, 275, 360, 305]]
        new_state, last_alert = self.eye_strain_prevention._check_tension(
            boxes,
            relaxed_ratios,
            ratio_history,
            "Relaxed face",
            0
        )

        self.assertEqual(new_state, "Relaxed face")


if __name__ == '__main__':
    unittest.main()
