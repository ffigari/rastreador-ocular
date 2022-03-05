from datetime import datetime, timedelta

def date_iso_string_to_datetime(date_string):
    return datetime.fromisoformat(date_string.replace("Z", "+00:00"))

def distance_in_ms(oneDatetime, anotherDatetime):
    return (oneDatetime - anotherDatetime).total_seconds() * 1000

SAMPLING_DELTA = timedelta(0, 0.1)
