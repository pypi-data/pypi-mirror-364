import re
from typing import ClassVar

class HumanTimeConverter:
    """
    A reusable class for converting between seconds and human-readable time strings.
    Extendable for additional units (e.g., ms, days).
    """
    # Regex pattern for parsing human-readable time
    TIME_PATTERN: ClassVar[re.Pattern] = re.compile(r"(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?")

    @classmethod
    def seconds_to_human(cls, seconds: int) -> str:
        """
        Convert seconds to a human-readable time string (e.g., '1h 2m 3s').
        """
        if not isinstance(seconds, int) or seconds < 0:
            raise ValueError("Seconds must be a non-negative integer.")
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        parts = []
        if h > 0:
            parts.append(f"{h}h")
        if m > 0:
            parts.append(f"{m}m")
        if s > 0 or not parts:
            parts.append(f"{s}s")
        return " ".join(parts)

    @classmethod
    def human_to_seconds(cls, human_time: str) -> int:
        """
        Convert a human-readable time string (e.g., '1h 2m 3s') to seconds.
        """
        if not isinstance(human_time, str):
            raise ValueError("Input must be a string.")
        if not human_time.strip():
            raise ValueError("Input string is empty.")
        match = cls.TIME_PATTERN.fullmatch(human_time.strip())
        if not match:
            raise ValueError(f"Invalid time string: '{human_time}'")
        h, m, s = match.groups(default="0")
        return int(h) * 3600 + int(m) * 60 + int(s)
