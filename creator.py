"""
from creator import *
d = {'zoomId': '6038224458', 'zoomPasswordId': 'bDhDL3ZVR29ydWVKMWZoRS9CMWxsQT09', 'sketchcodes': 'sc/S2-AE2B.tsv'}
ld = datetime.datetime(2020, 12, 18)
fd = datetime.datetime(2020, 10, 26)
add_courses('course_574', fd, ld, d, ('Mon', '8am', '9:50am'), ('Tues', '8am', '9:50am'), ('Wed', '8am', '9:50am'), ('Thur', '8am', '9:50am'), ('Fri', '8am', '9:50am'))
"""

from time import sleep
import datetime
from collections import defaultdict
from dateutil.parser import parse
from canvasapi import Canvas
from planner import date_range, session_range


SL_HOLIDAYS = (datetime.datetime(2020, 11, 11),   # veterans day
               datetime.datetime(2020, 11, 12),
               datetime.datetime(2020, 11, 19),
               datetime.datetime(2020, 12, 3),
               datetime.datetime(2020, 12, 10),
               datetime.datetime(2020, 11, 26),   # thanksgiving
               datetime.datetime(2020, 11, 27),)  # thanksgiving

# loads file containing API keys
with open('api_credentials.txt') as f:
    API_URL, API_KEY = f.read().splitlines()

# creates class for Canvas API wrapper
canvas = Canvas(API_URL, API_KEY)



def get_sketchcodes(sketchcode_f, with_titles=False):
    with open(sketchcode_f) as f:
        sketchcodes = f.read()
    if with_titles:
        return [line.replace("\t'", "\t").split() for line in sketchcodes.splitlines() if line]

    return [line.split()[-1].replace("'", '') for line in sketchcodes.splitlines() if line]


def objs_by_day(course_id):
    course = [c for c in canvas.get_courses() if c.id == course_id]
    if not course:
        return None
    else:
        course = course[0]

    objs = defaultdict(list)

    for assignment in course.get_assignments():
        if assignment.due_at:
            print(assignment.due_at[:10])
            objs[assignment.due_at[:10]].append(assignment)
    for event in canvas.get_calendar_events(context_codes=['course_' + str(course_id)], all_events=True):
        if event.start_at:
            print(event.start_at[:10])
            objs[event.start_at[:10]].append(event)

    return objs






def change_all_dates(context_code, first_day, last_day, description_data, *times, lesson_i=1, prefix='LD', holidays=SL_HOLIDAYS, sleep_t=.5):
    assert type(description_data) == dict, 'Description must be dict'

    sketchcodes = get_sketchcodes(description_data['sketchcodes']) if description_data.get('sketchcodes', None) else None
    # converts strings to datetime objects
    if type(first_day) == str:
        first_day = parse(first_day)
    if type(last_day) == str:
        last_day = parse(last_day)

    # creates range of dates from first_day to last_day
    dates = date_range(first_day, last_day)
    # makes a list of class sessions based on the dates list and the *times argument(s)
    sessions = session_range(dates, *times, holidays=holidays)





def add_courses(context_code, first_day, last_day, description_data, *times, lesson_i=1, prefix='LD', holidays=SL_HOLIDAYS, sleep_t=.5):
    """
    Arguments:
        context_code: context code argument passed to canvas API -- must be string
        first_day: the first day of the class as a string or datetime object -- must include day, month, and year
        first_day: the last day of the class as a string or datetime object -- must include day, month, and year
        description: A dictionary with keys: zoomId, zoomPasswordId, and sketchcodes. The sketchcodes key
        must be a path to a tsv containing the sketchdoes for the class.
        *times: a tuple of the day, start time, and end time of classes e.g. ('Monday', '8am', '10am')
    Keyword Arguments:
        lesson_i: the lesson number to begin with (used in event title e.g. LD: Lesson 07)
        holidays: a tuple of strings of holiday dates -- these dates are not included in the output -- or None

    Adds lessons on MW from 2pm-3pm from 10/19/2020 to 11/20/2020
    >>> from creator import *
    >>> d = {'zoomId': '12345678', 'zoomPasswordId': 'abc123', 'sketchcodes': 'mycodes.tsv'}
    >>> add_courses('course_574', '10/19/2020', '11/20/2020', d, ('Mon', '2pm', '3pm'), ('Wed', '2pm', '3pm'))
    """

    assert type(description_data) == dict, 'Description must be dict'

    sketchcodes = get_sketchcodes(description_data['sketchcodes']) if description_data.get('sketchcodes', None) else None


    # converts strings to datetime objects
    if type(first_day) == str:
        first_day = parse(first_day)
    if type(last_day) == str:
        last_day = parse(last_day)

    # creates range of dates from first_day to last_day
    dates = date_range(first_day, last_day)
    # makes a list of class sessions based on the dates list and the *times argument(s)
    sessions = session_range(dates, *times, holidays=holidays)

    # adds sessions to calendar
    for start_at, end_at in sessions:
        # makes description
        description = '<p>zoomId: {zid}</p><p>sketchId: {sid}</p><p>zoomPasswordId: {zpwid}</p>'.format(
            zid=description_data.get('zoomId', ''),
            sid=sketchcodes[lesson_i-1],
            zpwid=description_data.get('zoomPasswordId', '')
        )

        # makes title
        title = '{prefix}: Lesson {lesson_i:02d}'.format(prefix=prefix, lesson_i=lesson_i)
        lesson_i += 1   # The description uses this to pick a sketch code, so don't increment until after desc is made

        # dictionary that gets sent to the Canvas API
        lesson_data = {'context_code' : context_code, 'title': title, 'start_at': start_at, 'end_at': end_at, 'description': description}
        # sends data to API
        canvas.create_calendar_event(lesson_data)
        print(context_code, title)
        sleep(sleep_t)
