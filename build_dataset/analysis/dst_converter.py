from datetime import datetime as dt

def dst_converter(ts):
    date = dt.fromtimestamp(ts)
    if date.month <= 3 and date.day <= 30:
        return ts
    if date.month >= 10 and date.day >= 26:
        return ts
    else:
        return ts + 3600