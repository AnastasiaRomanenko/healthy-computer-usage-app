import time
from backend.core.notification_manager import NotificationManager


class BreakReminders:
    # remind users to take regular breaks following the 20-20-20 rule and longer breaks
    BREAK_INTERVAL = 20 * 60  # 20 minutes - look away for 20 seconds

    def __init__(self):
        self.notifier = NotificationManager()

    def monitor(self):
        # monitor time and send break reminders
        try:
            while True:
                time.sleep(self.BREAK_INTERVAL)

                message = "Time for a 20-second eye break!"
                self.notifier.send("Look at something 20 feet away", message)

                print("Notification was sent")

        except KeyboardInterrupt:
            print("\n\nBreak reminders monitor stopped")


def main():
    break_reminders = BreakReminders()
    break_reminders.monitor()


if __name__ == "__main__":
    main()
