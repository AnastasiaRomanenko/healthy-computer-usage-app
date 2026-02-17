import cv2
from typing import Optional, Tuple
from .notification_manager import NotificationManager


class CameraManager:
    # manages camera
    def __init__(self):
        self.notifier = NotificationManager()
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_open = False

    def open(self, image_path: str, camera_index: int = 0) -> bool:
        # open camera
        if self.is_open:
            return True

        img = cv2.imread(image_path)
        if img is None:
            return False

        height, width = img.shape[:2]

        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            self.notifier.send("Error: Camera Access", "Could not open camera. Please check your camera settings.")
            return False

        if width and height:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.is_open = True
        return True

    def read(self) -> Tuple[bool, Optional[cv2.Mat]]:
        # read a frame from the camera
        if not self.is_open or self.cap is None:
            return False, None

        return self.cap.read()

    def release(self) -> None:
        # release camera resources
        if self.cap is not None:
            self.cap.release()
            self.is_open = False

    def __enter__(self):
        # context manager entry
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # release camera
        self.release()
