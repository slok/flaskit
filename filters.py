import datetime
import re
import jinja2

from pygments import highlight
from pygments.lexers import HtmlLexer, guess_lexer, guess_lexer_for_filename, get_lexer_by_name
from pygments.formatters import HtmlFormatter

def convert_unix_time_filter(unix_time, timeFormat=None):
    
    timeFormat = '%Y-%m-%d %H:%M:%S' if timeFormat is None else timeFormat
    
    return datetime.datetime.fromtimestamp(unix_time).strftime(timeFormat)


def truncate_hex_filter(hex_number, length):
        
    return hex_number[:length]

def get_email_from_commit_author_filter(author):
    m = re.match(r".*<(.+@.+\..+)>", author)
    
    if not m:
        return ''
    
    return m.group(1)

def get_author_from_commit_author_filter(author):
    m = re.match(r"(.*)<.+>", author)
    return m.group(1)

def pygmetize_by_name_filter(code, name):
    try:
        lexer = get_lexer_by_name(name)
    except:
        lexer = HtmlLexer()
        
    new_code = highlight(code, lexer, HtmlFormatter())
    return new_code

def pygmetize_by_filename_filter(code, fileName=None):
    try:
        #guess code language by code if there is not a filename
        if not fileName:
            lexer = guess_lexer(code)
        else:
            lexer = guess_lexer_for_filename(fileName, code)
    except:
        lexer = HtmlLexer()
        
    new_code = highlight(code, lexer, HtmlFormatter())
    return new_code


jinja2.filters.FILTERS['convert_unix_time'] = convert_unix_time_filter
jinja2.filters.FILTERS['truncate_hex'] = truncate_hex_filter
jinja2.filters.FILTERS['get_email_from_commit_author'] = get_email_from_commit_author_filter
jinja2.filters.FILTERS['get_author_from_commit_author'] = get_author_from_commit_author_filter
jinja2.filters.FILTERS['pygmetize_by_filename'] = pygmetize_by_filename_filter
jinja2.filters.FILTERS['pygmetize_by_name'] = pygmetize_by_name_filter

