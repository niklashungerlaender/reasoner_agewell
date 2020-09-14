from datetime import datetime, timedelta
from random import uniform
import _languagedicts as ld
import re



def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def next_weekday(weekday):
    d = datetime.now()
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    datetime_new = d + timedelta(days_ahead)
    return datetime_new.date()


def create_items_dict(content_display="", item_type="", item_id="", options=[]):
    options_list = [
        {"OPTION_ID": i + 1, "OPTION_TEXT": j}
        for i, j in enumerate(options)
    ]
    question_dict = {"CONTENT_DISPLAY": content_display, "TYPE": item_type, "ITEM_ID": item_id, "OPTIONS": options_list}
    return question_dict


def create_question_dict(content_display="", items=""):
    question_list = [
        {"ID": i + 1, "CONTENT_DISPLAY": j, "ITEMS": items[i]}
        for i, j in enumerate(content_display)
    ]
    return question_list


def create_buttons_dict(button_type="", content="", wait=False, tts="",
                        language_code="en"):
    button_dict = {"TYPE": button_type, "CONTENT_DISPLAY": ld.buttons[content][language_code], "WAIT_ON_SUBMIT": wait,
                   "TTS_ON_CLICK": tts}
    return button_dict


def update_notification_time(list_of_notification_ids, notification_time, reminder_time):
    import _schedule
    for i in list_of_notification_ids:
        _schedule.scheduler.modify_job(job_id=i[0],
                                       run_date=datetime.combine(i[1],
                                       get_reminder_time(notification_time, reminder_time)))

def get_reminder_time(reminder_type, reminder_id):
    reminder = {"morning": {"0": [6, 8], "1": [8, 10], "2": [10, 12], "not_defined": [9, 9]},
                "evening": {"0": [18, 20], "1": [20, 22], "2": [22, 24], "not_defined": [19, 19]}}
    random_time = round(
        uniform(reminder[reminder_type][str(reminder_id)][0], reminder[reminder_type][str(reminder_id)][1] - 0.01), 2)
    to_timedelta = timedelta(hours=random_time)
    to_time = (datetime.min + to_timedelta).time()
    return to_time


def string_formatting(input_string):
    rx = r"\.(?=\S)"
    s = input_string
    result = re.sub(rx, ". ", s)
    return result

def convert_to_string(mylist):
    mylist = [str(i) for i in mylist]
    return mylist
