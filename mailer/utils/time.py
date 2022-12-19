from datetime import datetime
import pytz


def now() -> datetime:
    return datetime.now().astimezone(pytz.UTC)
