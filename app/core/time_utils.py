from datetime import datetime
import pytz

BAHIA_TZ = pytz.timezone('America/Bahia')

def get_bahia_datetime():
    """Returns the current datetime in America/Bahia timezone."""
    return datetime.now(BAHIA_TZ)

def get_bahia_time_str():
    """Returns the current ISO formatted string in America/Bahia timezone."""
    return get_bahia_datetime().strftime('%Y-%m-%d %H:%M:%S')
