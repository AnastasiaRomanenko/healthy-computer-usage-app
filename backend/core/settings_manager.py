import json
import os
from typing import Any
from threading import Lock


class SettingsManager:
    # singleton for managing application settings
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/assets"
            self.settings_file = self.path + '/settings.json'
            self.default_settings = {
                "eye_strain_prevention_enable": False,
                "eye_strain_prevention_ratios": 60,
                "distance_check_enable": False,
                "distance_check_area": 0,
                "night_limit_enable": False,
                "night_limit_time": "22:00",
                "daily_limit_enable": False,
                "daily_limit_time": 4,
                "break_reminders_enable": False,
                "blue_light_filter_enable": False,
                "blue_light_filter_day": 0,
                "blue_light_filter_evening": 0,
                "blue_light_filter_night": 0,
            }
            self._settings = self.load()
            self._last_modification_time = self._get_modification_time()
            self.initialized = True

    def _get_modification_time(self) -> float:
        try:
            return os.path.getmtime(self.settings_file)
        except OSError:
            return 0

    def load(self) -> dict:
        # load settings from file
        if not os.path.exists(self.settings_file):
            self.save(self.default_settings)
            return self.default_settings.copy()

        with open(self.settings_file, "r") as f:
            return json.load(f)

    def save(self, settings: dict) -> None:
        # save settings to file
        with self._lock:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=4)
            self._settings = settings.copy()
            self._last_modification_time = self._get_modification_time()

    def get(self, key: str, default: Any = None) -> Any:
        # get a specific setting
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        # set a specific setting and save
        self._settings[key] = value
        self.save(self._settings)

    def is_feature_enabled(self, feature_name: str) -> bool:
        # check if a feature is enabled
        return self._settings.get(f"{feature_name}_enable", False)
