import datetime as dt


def utcnow_unix_timestamp_s() -> int:
    return int(dt.datetime.now().timestamp())
