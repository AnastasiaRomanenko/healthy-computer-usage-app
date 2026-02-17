# Sim - healthy computer usage app

**Sim** is an application that helps users maintain healthy computer habits.
It provides reminders, blue light filter and computer limitations, reduces eye strain, monitors healthy distance to the screen.
**Goal:** Reduce negative effects of inappropriate computer usage.

**Key features:**
* Eye strain detection – monitor expressions using available model
* Distance monitoring – monitor healthy distance to the screen by applying a trained custom model
* Daily limit – track daily usage
* Night usage limit – encourage healthy sleep at night
* Break reminders – “Every 20 minutes look at something 20-feet away for at least 20 seconds”
* Blue light filter – apply filter for 3 modes (Day, Evening and Night)

**Technologies:**
* Python — main backend logic, computer vision, notifications.
* JavaScript — frontend logic (these switching, features enabling/disabling, API communication)
* HTML / CSS — UI layout and styles.
* OpenCV (cv2) — camera capture, image preprocessing.
* Ultralytics YOLOv11 – detects bounding boxes for eye strain detection and distance monitoring.
* Roboflow – provided a dataset for training an eye strain detection model.
* Google Colab – an environment for training an eye strain detection model.
* NumPy — calculating average values for eye ratios and distance areas
* macOS Notification Center (via osascript) — notification system on the MacOS.
* Local JSON configuration file (settings.json) – storing settings.

**Distance monitoring:**

The system detects facial keypoints – nose, left eye and right eye – and computes the area of the triangle formed by these points. This area is stored as a baseline value. During real-time operation, the same triangle area is computed for the user’s detected face. If the area increases beyond a threshold relative to the baseline (by 20%), the system identifies that the user is too close to the screen. 
The formula to calculate the area: Area = 0.5 * [x₁*(y₂ − y₃) + x₂*(y₃ − y₁) + x₃*(y₁ − y₂)]

**Eye strain detection:**

The model for detecting eye strain was trained in Google Colab using the Ultralytics framework and a dataset prepared with Roboflow. During calibration, the user captures a relaxed face image. The system detects eye bounding boxes and computes a geometric ratio defined as bounding box width divided by height. These ratios are stored as baseline values. During monitoring the same ratios are computed continuously. An average value is calculated using the last 5 results. If the average ratio exceeds 20% of the baseline ratio, the system classifies the state as eye strain and triggers a notification. 

**Testing:**
* Automated backend testing, which verifies the correctness of Python modules responsible for decision logic, persistence and notifications. These tests are written using the unittest framework and executed with pytest.
* Automated user interface testing, which verifies that the Electron-based UI loads correctly and responds properly to user interaction. User interface testing was performed using Playwright. The tests launch the real application and simulate user interactions such as navigation between screens and interaction with UI elements. 

**How it works:**
1. The app starts with easy settings setup.
2. It uses webcam for distance monitoring and eye strain detection if these features are enabled.
3. It notifies users when they need to correct themselves.
4. It runs quietly without disturbing the user’s workflow.

**Benefits:**
* Protects user’s vision and eye health
* Promotes healthy computer use habits so that the user feels better and more productive
* Supports better sleep by limiting night usage
* Easy to customize and adjust anytime




