import datetime
import re
import jinja2


def convert_unix_time_filter(unix_time, timeFormat=None):
    
    timeFormat = '%Y-%m-%d %H:%M:%S' if timeFormat is None else timeFormat
    
    return datetime.datetime.fromtimestamp(unix_time).strftime(timeFormat)


def truncate_hex_filter(hex_number, length):
        
    return hex_number[:length]

def get_email_from_commit_author_filter(author):
    m = re.match(r".*<(.+@.+\..+)>", author)
    return m.group(1)

def get_author_from_commit_author_filter(author):
    m = re.match(r"(.*)<.+@.+\..+>", author)
    return m.group(1)

jinja2.filters.FILTERS['convert_unix_time'] = convert_unix_time_filter
jinja2.filters.FILTERS['truncate_hex'] = truncate_hex_filter
jinja2.filters.FILTERS['get_email_from_commit_author'] = get_email_from_commit_author_filter
jinja2.filters.FILTERS['get_author_from_commit_author'] = get_author_from_commit_author_filter
