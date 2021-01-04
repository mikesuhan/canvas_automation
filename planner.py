import datetime
from dateutil.parser import parse

def date_range(first_day=datetime.datetime(2021, 1, 11, 8, 30), last_day=datetime.datetime(2021, 5, 7, 8, 30)):
    delta = last_day - first_day
    return list(reversed([last_day - datetime.timedelta(days=x) for x in range(delta.days + 1)]))

def session_range(dates, *times, holidays=('jan 18 2020',)):
    """
    Filters a range of dates based on session times

    Arguments:
        dates: a list of datetime objects
        *times: a tuple of the day, start time, and end time of classes e.g. ('Monday', '8am', '10am'
    Keyword Arguments:
        holidays: a tuple of strings of holiday dates -- these dates are not included in the output
    """
    sessions = []
    if holidays is None: holidays = []
    for date in dates:
        # checks to make sure date isn't a holiday
        for holiday in holidays:
            if type(holiday) == str:
                holiday = parse(holiday)
            if holiday.day == date.day and holiday.month == date.month and holiday.year == holiday.year:
                break
        # continues if date is not a holiday
        else:
            day = date.strftime("%a").lower()
            for session in times:
                d, ts = session[0], session[1:]

                if d.lower().startswith(day):
                    start_t = parse(ts[0])
                    start_at = date.replace(hour=start_t.hour, minute=start_t.minute)
                    if len(ts) > 1:
                        end_t = parse(ts[1])
                        end_at = date.replace(hour=end_t.hour, minute=end_t.minute)
                    else:
                        end_at = None
                    sessions.append((start_at, end_at))

    return sessions




