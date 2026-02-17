import time
from datetime import datetime, timedelta

from backend.core.notification_manager import NotificationManager
from backend.core.settings_manager import SettingsManager
from backend.core.time_manager import TimeManager


class NightLimit:
    # monitor bedtime limits
    def __init__(self):
        self.time_manager = TimeManager()
        self.settings = SettingsManager()
        self.notifier = NotificationManager()

    def monitor(self):
        # monitor time and enforce night limit
        bedtime_str = self.settings.get("night_limit_time", "22:00")
        print(f"Bedtime set to: {bedtime_str}")

        while True:
            hour, minute = map(int, bedtime_str.split(':'))
            now = datetime.now()
            bedtime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            remaining_time = bedtime - now
            print("Remaining time: ", remaining_time)
            remaining_seconds = int(remaining_time.total_seconds())

            if remaining_seconds + timedelta(minutes=max(self.time_manager.WARNING_MINUTES)).total_seconds() < 0:
                remaining_time += timedelta(days=1)

            remaining_minutes = remaining_seconds // 60

            # display current status
            formatted_time = self.time_manager.format_time(remaining_seconds, "night")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Time until bedtime: {formatted_time}")

            # before bedtime - send warnings
            if remaining_seconds > 0:
                for warning_minute in self.time_manager.WARNING_MINUTES:
                    if remaining_minutes == warning_minute:
                        message = f"It's {warning_minute} minute(s) until your bedtime. Start wrapping up!"
                        self.notifier.send("Bedtime Reminder", message)
                        break

            # at bedtime (within 1 minute)
            elif remaining_seconds <= 0 and remaining_seconds > -60:
                message = f"It's {bedtime_str}! Time to get off the computer and rest."
                self.notifier.send("Bedtime!", message)
            # past bedtime
            else:
                # if bedtime has passed today, it refers to tomorrow
                if bedtime + timedelta(minutes=max(self.time_manager.WARNING_MINUTES)) < now:
                    bedtime += timedelta(days=1)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Time until bedtime: {formatted_time}")

                else:
                    minutes_over = abs(remaining_minutes)
                    for warning_minute in self.time_manager.WARNING_MINUTES:
                        if minutes_over == warning_minute:
                            message = f"You're {minutes_over} minute(s) past bedtime! Please shut down soon."
                            self.notifier.send("Past Bedtime!", message)

            time.sleep(self.time_manager.CHECK_INTERVAL)


def main():
    night_limit = NightLimit()
    night_limit.monitor()


if __name__ == "__main__":
    main()
