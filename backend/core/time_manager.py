class TimeManager:
    def __init__(self):
        self.CHECK_INTERVAL = 60  # check every 60 seconds
        self.WARNING_MINUTES = [120, 60, 30, 15, 5, 1]

    def format_time(self, seconds: int, type: str) -> str:
        # format timedelta
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        parts = []

        if seconds > 0:
            if hours > 0:
                parts.append(f"{hours} hour(s)")
            if minutes > 0:
                parts.append(f"{minutes} minute(s)")
        elif seconds < 0 and type == "daily":
            seconds = abs(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if hours > 0:
                parts.append(f"{hours} hour(s)")
            if minutes > 0:
                parts.append(f"{minutes} minute(s)")
        elif seconds < 0 and type == "night":
            hours += 24
            if hours > 0:
                parts.append(f"{hours} hours(s)")
            if minutes > 0:
                parts.append(f"{minutes} minutes(s)")

        if not parts:
            return "less than 1 minute"

        return " ".join(parts)
