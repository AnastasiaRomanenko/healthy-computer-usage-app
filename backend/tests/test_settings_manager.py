import unittest
import os
import json
import tempfile
from backend.core.settings_manager import SettingsManager


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.settings_file = os.path.join(self.test_dir, 'settings.json')

    def test_singleton_pattern(self):
        manager1 = SettingsManager()
        manager2 = SettingsManager()

        self.assertIs(manager1, manager2)

    def test_default_settings_creation(self):
        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        settings = manager.load()

        self.assertTrue(os.path.exists(self.settings_file))
        self.assertIsInstance(settings, dict)
        self.assertIn('eye_strain_prevention_enable', settings)

    def test_save_settings(self):
        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        test_settings = {
            "eye_strain_prevention_enable": False,
            "distance_check_enable": True,
            "night_limit_enable": True,
            "night_limit_time": "23:00",
            "daily_limit_enable": True,
            "daily_limit_time": "06:00",
            "break_reminders_enable": True,
            "blue_light_filter_enable": True,
            "blue_light_filter_day": 0,
            "blue_light_filter_evening": 40,
            "blue_light_filter_night": 80,
            "distance_check_area": 1011
        }

        manager.save(test_settings)
        self.assertTrue(os.path.exists(self.settings_file))

        with open(self.settings_file, 'r') as f:
            saved_settings = json.load(f)

        self.assertEqual(saved_settings, test_settings)

    def test_load_settings(self):
        test_settings = {
            "eye_strain_prevention_enable": False,
            "distance_check_enable": True,
            "night_limit_enable": True,
            "night_limit_time": "23:00",
            "daily_limit_enable": True,
            "daily_limit_time": "06:00",
            "break_reminders_enable": True,
            "blue_light_filter_enable": True,
            "blue_light_filter_day": 0,
            "blue_light_filter_evening": 40,
            "blue_light_filter_night": 80,
            "distance_check_area": 1011
        }

        with open(self.settings_file, 'w') as f:
            json.dump(test_settings, f)

        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        loaded_settings = manager.load()

        self.assertEqual(loaded_settings, test_settings)

    def test_get_setting(self):
        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        manager._settings = {
            'night_limit_time': '22:00',
            'daily_limit_time': "04:00"
        }

        self.assertEqual(manager.get('night_limit_time'), '22:00')
        self.assertEqual(manager.get('daily_limit_time'), "04:00")
        self.assertIsNone(manager.get('nonexistent_key'))

    def test_set_setting(self):
        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        manager.set('test_key', 'test_value')

        self.assertEqual(manager.get('test_key'), 'test_value')

        with open(self.settings_file, 'r') as f:
            saved_settings = json.load(f)

        self.assertEqual(saved_settings['test_key'], 'test_value')

    def test_is_feature_enabled(self):
        manager = SettingsManager()
        manager.path = self.test_dir
        manager.settings_file = self.settings_file

        manager._settings = {
            'eye_strain_prevention_enable': True,
            'distance_check_enable': False,
            'night_limit_enable': True
        }

        self.assertTrue(manager.is_feature_enabled('eye_strain_prevention'))
        self.assertFalse(manager.is_feature_enabled('distance_check'))
        self.assertTrue(manager.is_feature_enabled('night_limit'))
        self.assertFalse(manager.is_feature_enabled('nonexistent_feature'))


class TestSettingsManagerThreadSafety(unittest.TestCase):

    def test_concurrent_access(self):
        import threading

        instances = []

        def create_instance():
            manager = SettingsManager()
            instances.append(manager)

        threads = [threading.Thread(target=create_instance) for _ in range(10)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        first_instance = instances[0]
        for instance in instances:
            self.assertIs(instance, first_instance)


if __name__ == '__main__':
    unittest.main()
