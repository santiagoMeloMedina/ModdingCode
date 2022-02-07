import datetime
import enum
import pytz


class Timezone(enum.Enum):
    CO = "America/Bogota"


def get_unix_time_from_now(timezone: Timezone = Timezone.CO) -> int:
    now = datetime.datetime.now(tz=pytz.timezone(timezone.value))
    return int(now.timestamp())
