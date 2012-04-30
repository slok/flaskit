import datetime
import jinja2


def convert_unix_time_filter(unix_time, timeFormat=None):
    
    timeFormat = '%Y-%m-%d %H:%M:%S' if timeFormat is None else timeFormat
    
    return datetime.datetime.fromtimestamp(unix_time).strftime(timeFormat)


def truncate_hex_filter(hex_number, length):
    
    
    return hex_number[:length]



jinja2.filters.FILTERS['convert_unix_time'] = convert_unix_time_filter
jinja2.filters.FILTERS['truncate_hex'] = truncate_hex_filter
