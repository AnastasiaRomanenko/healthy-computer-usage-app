import unittest
import tempfile
import shutil
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
import os
from backend.core.camera_manager import CameraManager
from backend.core.notification_manager import NotificationManager


class TestCameraManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.test_dir, 'test_image.png')

        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite(self.test_image_path, test_img)

        NotificationManager._instance = None

        self.camera = CameraManager()

    def test_init(self):
        self.assertIsInstance(self.camera.notifier, NotificationManager)
        self.assertIsNone(self.camera.cap)
        self.assertFalse(self.camera.is_open)

    def test_open_with_invalid_image_path(self):
        result = self.camera.open('nonexistent_image.png')

        self.assertFalse(result)
        self.assertFalse(self.camera.is_open)

    @patch('cv2.VideoCapture')
    def test_open_success(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        result = self.camera.open(self.test_image_path)

        self.assertTrue(result)
        self.assertTrue(self.camera.is_open)
        mock_video_capture.assert_called_once_with(0)
        mock_cap.set.assert_called()

    @patch('subprocess.run')
    @patch('cv2.VideoCapture')
    def test_open_camera_not_available(self, mock_video_capture, mock_subprocess):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap

        result = self.camera.open(self.test_image_path)

        self.assertFalse(result)
        self.assertFalse(self.camera.is_open)
        self.assertEqual(mock_subprocess.call_count, 1)

    def test_read_without_opening(self):
        success, frame = self.camera.read()

        self.assertFalse(success)
        self.assertIsNone(frame)

    @patch('cv2.VideoCapture')
    def test_read_success(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_video_capture.return_value = mock_cap

        self.camera.open(self.test_image_path)
        success, frame = self.camera.read()

        self.assertTrue(success)
        self.assertIsNotNone(frame)
        mock_cap.read.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_release(self, mock_video_capture):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap

        self.camera.open(self.test_image_path)
        self.assertTrue(self.camera.is_open)

        self.camera.release()

        self.assertFalse(self.camera.is_open)
        mock_cap.release.assert_called_once()


class TestCameraManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        NotificationManager._instance = None

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        NotificationManager._instance = None

    def test_multiple_open_close_cycles(self):
        camera = CameraManager()
        test_image = os.path.join(self.test_dir, 'test.png')

        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite(test_image, img)

        with patch('cv2.VideoCapture') as mock_capture:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_capture.return_value = mock_cap

            camera.open(test_image)
            self.assertTrue(camera.is_open)

            camera.release()
            self.assertFalse(camera.is_open)

            camera.open(test_image)
            self.assertTrue(camera.is_open)


if __name__ == '__main__':
    unittest.main()
