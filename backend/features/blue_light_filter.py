import time
import subprocess
from datetime import datetime

from backend.core.settings_manager import SettingsManager
from backend.core.notification_manager import NotificationManager


class BlueLightFilter:
    # adjust screen color temperature
    CHECK_INTERVAL = 60  # check every 60 seconds

    DAY_START = 6
    EVENING_START = 18
    NIGHT_START = 21

    def __init__(self):
        self.settings = SettingsManager()
        self.notifier = NotificationManager()
        self.current_period = None
        self.last_notification_period = None

    def get_current_period(self) -> str:
        # determine current time period
        # hour = (datetime.now() + timedelta(hours=10)).hour
        hour = datetime.now().hour
        if self.DAY_START <= hour < self.EVENING_START:
            return "day"
        elif self.EVENING_START <= hour < self.NIGHT_START:
            return "evening"
        else:
            return "night"

    def apply_filter(self, period: str, percentage: int):

        result = subprocess.run(["which", "nightlight"], capture_output=True, text=True)

        if not result.returncode == 0:
            subprocess.run(["brew", "install", "smudge/smudge/nightlight"], check=True, capture_output=True)
            return

        subprocess.run(["nightlight", "on"], check=True, capture_output=True)

        subprocess.run(["nightlight", "temp", str(percentage)], check=True, capture_output=True)

        # Send notification on period change
        if self.last_notification_period != period:
            messages = {
                "day": f"Day mode is active: {percentage}%",
                "evening": f"Evening mode is active: {percentage}%",
                "night": f"Night mode is active: {percentage}%"
            }

            self.notifier.send("Blue Light Filter", messages[period])
            self.last_notification_period = period

    def monitor(self):
        # monitor time and adjust blue light filter

        # apply initial filter
        current_period = self.get_current_period()
        current_percentage = self.settings.get(f"blue_light_filter_{current_period}", 0)
        self.apply_filter(current_period, current_percentage)
        self.current_period = current_period

        try:
            while True:
                # check if time period changed
                new_period = self.get_current_period()
                if new_period != self.current_period:
                    new_percentage = self.settings.get(f"blue_light_filter_{new_period}", "0")
                    self.apply_filter(new_period, new_percentage)
                    self.current_period = new_period

                time.sleep(self.CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n\n Blue light filter monitor stopped")
            subprocess.run(["nightlight", "off"], check=True, capture_output=True)


def main():
    # main entry point for blue light filter feature
    blue_light = BlueLightFilter()
    blue_light.monitor()
    subprocess.run(["nightlight", "off"], check=True, capture_output=True)


if __name__ == "__main__":
    main()
