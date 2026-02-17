import subprocess
import time
from typing import Dict, Tuple
from threading import Lock


class NotificationManager:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, default_cooldown: int = 5):
        if not hasattr(self, 'initialized'):
            self.default_cooldown = default_cooldown
            self.last_notifications: Dict[Tuple[str, str], float] = {}
            self.initialized = True

    def send(self, title: str, message: str) -> bool:
        # send notification with cooldown
        now = time.time()
        key = (title, message)

        if key in self.last_notifications:
            if now - self.last_notifications[key] < self.default_cooldown:
                return False

        self.last_notifications[key] = now
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])
        return True
