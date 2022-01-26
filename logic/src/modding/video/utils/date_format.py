import datetime


def get_now_unix_time() -> int:
    now = datetime.datetime.now()
    return int(now.timestamp())
