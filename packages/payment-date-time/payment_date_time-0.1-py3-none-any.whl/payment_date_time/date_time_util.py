# senddatetime/datetime_util.py

from datetime import datetime

def get_current_datetime():
    """
    Returns the current datetime as a formatted string.
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
