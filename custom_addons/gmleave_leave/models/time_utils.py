from datetime import datetime, timedelta


def float_to_time(value):
    td = timedelta(hours=float(value))
    dt = datetime.min + td
    return '{:%H:%M}'.format(dt)
