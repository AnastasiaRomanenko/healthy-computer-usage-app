import os
import cv2
import numpy as np
import time
from ultralytics import YOLO
from collections import deque

from backend.core.notification_manager import NotificationManager
from backend.core.camera_manager import CameraManager
from backend.core.settings_manager import SettingsManager


class EyeStrainPrevention:
    # monitor user's eye strain from screen using eyes detection
    ALERT_COOLDOWN = 5
    DETECTION_CONFIDENCE = 0.1
    TENSION_THRESHOLD = 1.2  # 20% strain than relaxed image
    HISTORY_SIZE = 5

    def __init__(self):
        self.settings = SettingsManager()
        self.notifier = NotificationManager()
        self.camera = CameraManager()

        self.RELAXED_IMAGE = self.settings.path + "/relaxed_face.png"
        self.model = YOLO(self.settings.path + '/best_model.pt')

    def calibrate(self) -> bool:
        # Get healthy ratio by detecting eyes in relaxed image
        if not os.path.exists(self.RELAXED_IMAGE):
            self.notifier.send(
                "Error: Eye Strain Prevention",
                "Relaxed image not found. Please provide the image to continue."
            )
            return False

        results = self.model.predict(source=self.RELAXED_IMAGE, conf=0.5)

        boxes = results[0].boxes

        if len(boxes) < 2:
            self.notifier.send("Error: Eyes Detection",
                               "Please ensure both eyes are visible")
            return False
        elif len(boxes) > 2:
            self.notifier.send("Error: Eyes Detection",
                               "Please ensure only your eyes are visible")
            return False

        ratios = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            ratio = (x2 - x1) / (y2 - y1)
            ratios.append(ratio)

        self.settings.set("eye_strain_prevention_ratios", ratios)
        return True

    def monitor(self):
        # monitor ratios in real-time and alert user has eye strain
        relaxed_ratios = self.settings.get("eye_strain_prevention_ratios", [])
        if relaxed_ratios is None:
            self.notifier.send(
                "Error: Eye Strain Prevention",
                "Please provide your relaxed image first"
            )
            return

        if not os.path.exists(self.RELAXED_IMAGE):
            self.notifier.send(
                "Error: Eye Strain Prevention",
                "Relaxed image not found. Please provide the image to continue."
            )
            return

        if not self.camera.open(self.RELAXED_IMAGE):
            self.notifier.send(
                "Error: Camera Error",
                "Couldn't open the camera."
            )
            return

        ratios_history = [deque(maxlen=self.HISTORY_SIZE), deque(maxlen=self.HISTORY_SIZE)]
        not_visible_eyes = deque(maxlen=self.HISTORY_SIZE)
        too_many_eyes = deque(maxlen=self.HISTORY_SIZE)
        last_alert_time = 0
        tension_state = "Relaxed face"
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to receive frame.")
                    self.notifier.send(
                        "Error: Eye Strain Prevention",
                        "Failed to receive frame."
                    )
                    break

                frame = cv2.flip(frame, 1)  # Mirror the frame
                results = self.model.predict(frame, conf=self.DETECTION_CONFIDENCE)
                boxes = results[0].boxes

                # handle different detection scenarios
                if len(boxes) < 2:
                    self._handle_no_eyes_detected(not_visible_eyes)
                elif len(boxes) > 2:
                    self._handle_multiple_eyes(too_many_eyes)
                else:
                    print("Boxes: ", results[0].boxes)
                    print("Relaxed ratios: ", relaxed_ratios)
                    print("Ratios history: ", ratios_history)

                    # single pair of eyes detected - check ratios

                    boxes = [boxes[0].xyxy[0].tolist(), boxes[1].xyxy[0].tolist()]
                    tension_state, last_alert_time = self._check_tension(
                        boxes,
                        relaxed_ratios,
                        ratios_history,
                        tension_state,
                        last_alert_time
                    )

                cv2.imshow('Eye Strain Prevention - Press q to Quit', frame)
                time.sleep(5)
                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            self.camera.release()
            cv2.destroyAllWindows()

    def _handle_no_eyes_detected(self, not_visible_eyes: deque):
        # no eyes are detected
        not_visible_eyes.append(time.time())

        if len(not_visible_eyes) == self.HISTORY_SIZE:
            time_span = not_visible_eyes[-1] - not_visible_eyes[0]
            if time_span > 5:  # eyes not visible for 5+ seconds
                self.notifier.send(
                    "Error: Eyes Detection",
                    "Please ensure your eyes are visible in the camera."
                )

    def _handle_multiple_eyes(self, too_many_eyes: deque):
        # handle case when multiple eyes are detected
        too_many_eyes.append(time.time())

        if len(too_many_eyes) == self.HISTORY_SIZE:
            time_span = too_many_eyes[-1] - too_many_eyes[0]
            if time_span > 5:  # multiple eyes detected for 5 seconds
                self.notifier.send(
                    "Error: Eyes Detection",
                    "Please ensure only your eyes are visible in the camera."
                )

    def _check_tension(self, boxes, relaxed_ratios: list, ratios_history: list, tension_state: str, last_alert_time: float) -> tuple[str, float]:
        # check if user has healthy ratio
        print("Boxes: ", boxes)
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes[i]
            current_ratio = (x2 - x1) / (y2 - y1)

            ratios_history[i].append(current_ratio)
            avg_ratio = np.mean(ratios_history[i])

            if avg_ratio > self.TENSION_THRESHOLD * relaxed_ratios[i]:
                new_state = "Focused face"
            else:
                new_state = "Relaxed face"

            now = time.time()

            if new_state != tension_state or (now - last_alert_time > self.ALERT_COOLDOWN):
                if new_state == "Focused face":
                    self.notifier.send(
                        "Tension Alert",
                        "You are too focused! Relax your face first.")
                    last_alert_time = now

            tension_state = new_state

        return tension_state, last_alert_time


def main():
    # entry point for eye strain prevention feature
    eye_strain_prevention = EyeStrainPrevention()
    settings = SettingsManager()
    # Check if calibration is needed
    if settings.get("eye_strain_prevention_ratios") is None:
        if os.path.exists(eye_strain_prevention.RELAXED_IMAGE):
            if not eye_strain_prevention.calibrate():
                return
        else:
            return
    eye_strain_prevention.monitor()


if __name__ == "__main__":
    main()
