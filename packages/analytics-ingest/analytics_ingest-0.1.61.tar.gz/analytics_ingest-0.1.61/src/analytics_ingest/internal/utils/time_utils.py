from datetime import datetime


UNIX = datetime(1970, 1, 1)
ICS_EPOCH = datetime(2007, 1, 1)
DELTA = ICS_EPOCH - UNIX


def adjust_time_val(db_time_val):
    timestamp = datetime.utcfromtimestamp(db_time_val)
    timestamp += DELTA
    return timestamp


def parse_time_val(db_time_val):
    timestamp = adjust_time_val(db_time_val)
    try:
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
    except:
        db_time_val = db_time_val
        timestamp = datetime.utcfromtimestamp(db_time_val)
        timestamp += DELTA
        today = datetime.today()
        timestamp = timestamp.replace(year=today.year)
        return timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
