import os
import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import deque

from backend.core.notification_manager import NotificationManager
from backend.core.camera_manager import CameraManager
from backend.core.settings_manager import SettingsManager


class DistanceCheck:
    # monitor user's distance from screen using face detection
    ALERT_COOLDOWN = 5
    DETECTION_CONFIDENCE = 0.1
    DISTANCE_THRESHOLD = 1.2  # 20% closer than calibrated distance
    HISTORY_SIZE = 5

    def __init__(self):
        self.settings = SettingsManager()
        self.notifier = NotificationManager()
        self.camera = CameraManager()

        self.CALIBRATION_IMAGE = self.settings.path + "/calibrate_distance.png"
        self.model = YOLO(self.settings.path + "/yolo11n-pose.pt")

    def calibrate(self) -> bool:
        # Calibrate healthy distance by detecting face area in calibration image

        if not os.path.exists(self.CALIBRATION_IMAGE):
            self.notifier.send(
                "Error: Distance Check",
                "Calibration image not found. Please provide the image to continue."
            )
            return False

        results = self.model.predict(source=self.CALIBRATION_IMAGE, conf=0.5)

        if len(results) == 0:
            self.notifier.send("Error: Face Detection", "No face detected in calibration image")
            return False

        if len(results) > 1:
            self.notifier.send("Error: Face Detection",
                               "Multiple faces detected. Please ensure only your face is visible")
            return False

        # Calculate face area
        keypoints = results[0].keypoints.data
        keypoints = keypoints[0].cpu().numpy()

        nose = keypoints[0]
        left_eye = keypoints[1]
        right_eye = keypoints[2]

        print("Keypoints here:", keypoints)
        print("Result for nose: ", nose)
        print("Result for left eye: ", left_eye)
        print("Result for right eye: ", right_eye)

        area = abs(0.5 * (
            nose[0] * (left_eye[1] - right_eye[1])
            + left_eye[0] * (right_eye[1] - nose[1])
            + right_eye[0] * (nose[1] - left_eye[1])))

        print(f'Area: {area:.2f}')

        self.settings.set("distance_check_area", int(area))
        print(f'Healthy distance area saved: {int(area)}')

        return True

    def monitor(self):
        # monitor distance in real-time and alert user if too close

        healthy_area = self.settings.get("distance_check_area", 0)

        if healthy_area == 0:
            self.notifier.send(
                "Error: Distance Check",
                "Please calibrate your healthy distance first"
            )
            return

        if not os.path.exists(self.CALIBRATION_IMAGE):
            self.notifier.send(
                "Error: Distance Check",
                "Calibration image not found. Please provide the image to continue."
            )
            return

        if not self.camera.open(self.CALIBRATION_IMAGE):
            return

        area_history = deque(maxlen=self.HISTORY_SIZE)
        not_visible_face = deque(maxlen=self.HISTORY_SIZE)
        too_many_faces = deque(maxlen=self.HISTORY_SIZE)
        last_alert_time = 0
        distance_state = "Healthy distance"

        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to receive frame.")
                    self.notifier.send(
                        "Error: Distance Check",
                        "Failed to receive frame."
                    )
                    break

                frame = cv2.flip(frame, 1)  # Mirror the frame
                results = self.model.predict(frame, conf=self.DETECTION_CONFIDENCE)
                results = results[0]

                # handle different detection scenarios
                if len(results) < 1:
                    self._handle_no_face_detected(not_visible_face)
                elif len(results) > 1:
                    self._handle_multiple_faces(too_many_faces)
                else:
                    data = results[0].keypoints.data
                    keypoints = data[0].cpu().numpy()
                    # single face detected - check distance
                    distance_state, last_alert_time = self._check_distance(
                        keypoints,
                        healthy_area,
                        area_history,
                        distance_state,
                        last_alert_time
                    )

                # cv2.imshow('Distance Monitor - Press q to Quit', frame)
                time.sleep(5)
                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

    def _handle_no_face_detected(self, not_visible_face: deque):
        # no face is detected
        not_visible_face.append(time.time())

        if len(not_visible_face) == self.HISTORY_SIZE:
            time_span = not_visible_face[-1] - not_visible_face[0]
            if time_span > 5:  # face not visible for 5+ seconds
                self.notifier.send(
                    "Error: Face Detection",
                    "Please ensure your face is visible in the camera."
                )

    def _handle_multiple_faces(self, too_many_faces: deque):
        # handle case when multiple faces are detected
        too_many_faces.append(time.time())

        if len(too_many_faces) == self.HISTORY_SIZE:
            time_span = too_many_faces[-1] - too_many_faces[0]
            if time_span > 5:  # multiple faces detected for 5 seconds
                self.notifier.send(
                    "Error: Face Detection",
                    "Please ensure only your face is visible in the camera."
                )

    def _check_distance(self, keypoints, healthy_area: float, area_history: deque, distance_state: str, last_alert_time: float) -> tuple[str, float]:
        # check if user is at healthy distance
        nose = keypoints[0]
        left_eye = keypoints[1]
        right_eye = keypoints[2]

        current_area = abs(0.5 * (
            nose[0] * (left_eye[1] - right_eye[1])
            + left_eye[0] * (right_eye[1] - nose[1])
            + right_eye[0] * (nose[1] - left_eye[1])))

        area_history.append(current_area)
        avg_area = np.mean(area_history)

        print(f'Current Area: {avg_area:.2f}, Healthy Area: {healthy_area:.2f}')

        # Determine new state
        if avg_area > self.DISTANCE_THRESHOLD * healthy_area:
            new_state = "Too close"
        else:
            new_state = "Healthy distance"

        now = time.time()

        if new_state != distance_state or (now - last_alert_time > self.ALERT_COOLDOWN):
            if new_state == "Too close":
                self.notifier.send(
                    "Distance Alert",
                    "You are too close! Move back a bit.")
                last_alert_time = now

            distance_state = new_state

        return distance_state, last_alert_time


def main():
    # entry point for distance check feature
    distance_check = DistanceCheck()
    settings = SettingsManager()

    # Check if calibration is needed
    if settings.get("distance_check_area", 0) == 0:
        if os.path.exists(distance_check.CALIBRATION_IMAGE):
            if distance_check.calibrate():
                print("Calibration successful")
            else:
                print("Calibration failed")
                return
        else:
            print(f"Calibration image not found: {distance_check.CALIBRATION_IMAGE}")
            return
    distance_check.monitor()


if __name__ == "__main__":
    main()
