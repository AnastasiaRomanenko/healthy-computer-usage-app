import os
import time
import json
from datetime import datetime
from backend.core.settings_manager import SettingsManager
from backend.core.notification_manager import NotificationManager
from backend.core.time_manager import TimeManager


class DailyLimit:
    # track daily screen time limits

    def __init__(self):
        self.time_manager = TimeManager()
        self.settings = SettingsManager()
        self.notifier = NotificationManager()

        self.USAGE_DATA_FILE = self.settings.path + '/daily_usage.json'

    def load_usage_data(self) -> dict:
        # load daily usage data from file
        if not os.path.exists(self.USAGE_DATA_FILE):
            return self.create_new_usage_data()

        with open(self.USAGE_DATA_FILE, 'r') as f:
            data = json.load(f)

        # check if data is from today
        data_date = datetime.fromisoformat(data.get('date', ''))
        today = datetime.now().date()

        if data_date.date() != today:
            # new day - reset usage
            print("New day detected - resetting usage counter")
            return self.create_new_usage_data()

        return data

    def create_new_usage_data(self) -> dict:
        # create new usage data for today
        return {
            'date': datetime.now().isoformat(),
            'seconds_used': 0,
            'session_start': datetime.now().isoformat()
        }

    def monitor(self):
        # monitor daily usage and enforce limits
        daily_limit_str = self.settings.get("daily_limit_time", "04:00")

        print(f"Daily limit set to: {daily_limit_str}")

        print(f"Checking every {self.time_manager.CHECK_INTERVAL} seconds")
        print(f"Usage data file: {self.USAGE_DATA_FILE}")
        print("Press Ctrl+C to stop\n")

        session_start = datetime.now()
        usage_data = self.load_usage_data()
        try:
            while True:
                hour, minute = map(int, daily_limit_str.split(':'))
                now = datetime.now()
                daily_limit = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                session_duration_seconds = int((now - session_start).total_seconds())

                # update total usage
                usage_data['seconds_used'] += session_duration_seconds
                session_start = now  # reset session start for next interval

                # save usage data
                usage_data['date'] = now.isoformat()
                with open(self.USAGE_DATA_FILE, 'w') as f:
                    json.dump(usage_data, f, indent=4)

                used_total_seconds = usage_data['seconds_used']

                used_hours = used_total_seconds // 3600
                used_minutes = (used_total_seconds % 3600) // 60
                used_seconds = used_total_seconds % 60

                used_time = now.replace(hour=used_hours, minute=used_minutes, second=used_seconds, microsecond=0)

                remaining_time = daily_limit - used_time
                remaining_seconds = remaining_time.total_seconds()
                remaining_minutes = remaining_seconds // 60
                formatted_used_seconds = self.time_manager.format_time(int(used_total_seconds), "daily")
                formatted_total_seconds = self.time_manager.format_time(int(hour * 60 * 60 + minute * 60), "daily")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Used: {formatted_used_seconds} / {formatted_total_seconds}")

                # before limit reached
                formatted_remaining_time = self.time_manager.format_time(int(remaining_seconds), "daily")

                if remaining_seconds > 0:
                    # send warnings for time left
                    for warning_min in self.time_manager.WARNING_MINUTES:
                        if remaining_minutes == warning_min:
                            message = f"You have {formatted_remaining_time} of screen time left today"
                            self.notifier.send("Screen Time Alert", message)
                            break

                # at limit (within 1 minute)
                elif remaining_seconds <= 0 and remaining_seconds > -60:
                    message = "You've reached your daily screen time limit! Time to take a break."
                    self.notifier.send("Daily Limit Reached", message)

                # over limit
                else:
                    minutes_over = abs(int(remaining_minutes))
                    for warning_minute in self.time_manager.WARNING_MINUTES:
                        if minutes_over == warning_minute:
                            message = f"You're {minutes_over} minute(s) over your daily limit! Please shut down soon."
                            self.notifier.send("Over Daily Limit", message)

                time.sleep(self.time_manager.CHECK_INTERVAL)

        except KeyboardInterrupt:
            # save final usage before exiting
            session_duration = int((datetime.now() - session_start).total_seconds())
            usage_data['seconds_used'] += session_duration
            with open(self.USAGE_DATA_FILE, 'w') as f:
                json.dump(usage_data, f, indent=4)


def main():
    daily_limit = DailyLimit()
    daily_limit.monitor()


if __name__ == "__main__":
    main()
