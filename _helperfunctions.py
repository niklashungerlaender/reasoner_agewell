from datetime import datetime, timedelta
from random import uniform
import _languagedicts as ld
import re
import pyphen
import numpy as np
from functools import partial


class StoreInput:
    notification_dict = dict()

    def __init__(self, notification_id, name=None, value=None):
        self.notification_id = str(notification_id)
        self.name = name
        self.value = value
        if self.notification_id not in self.notification_dict.keys():
            self.notification_dict[self.notification_id] = {}

    def add_value(self):
        self.notification_dict[self.notification_id][self.name] = self.value

    def append_value(self):
        if self.name not in self.notification_dict[self.notification_id].keys():
            self.notification_dict[self.notification_id][self.name] = [self.value]
        else:
            self.notification_dict[self.notification_id][self.name].append(self.value)

    def get_value(self):
        return self.notification_dict[self.notification_id][self.name]

    def delete_entry(self):
        del self.notification_dict[self.notification_id]


def get_hyphenation(text, language):
    dic = pyphen.Pyphen(lang=language)
    hyphenated = dic.inserted(text)
    return str(hyphenated)


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
                        language_code="en", open_activity=None):
    if open_activity is None:
        button_dict = {"TYPE": button_type, "CONTENT_DISPLAY": ld.buttons[content][language_code],
                       "WAIT_ON_SUBMIT": wait, "TTS_ON_CLICK": tts}
    else:
        button_dict = {"TYPE": button_type, "CONTENT_DISPLAY": ld.buttons[content][language_code], "WAIT_ON_SUBMIT": wait,
                       "TTS_ON_CLICK": tts, "OPEN_ACTIVITY": open_activity}
    return button_dict


def update_notification_time(list_of_notification_ids, time_of_day, new_time):
    import _schedule
    for i in list_of_notification_ids:
        _schedule.scheduler.reschedule_job(job_id=i[0],
                                           run_date=datetime.combine(datetime.utcfromtimestamp(i[1]),
                                           get_reminder_time(time_of_day, new_time)))


def get_reminder_time(reminder_type, reminder_id):
    reminder = {"morning": {"0": [6, 8], "1": [8, 10], "2": [10, 12], "not_defined": [9, 9]},
                "evening": {"0": [18, 20], "1": [20, 22], "2": [22, 24], "not_defined": [19, 19]}}
    random_time = round(
        uniform(reminder[reminder_type][str(reminder_id)][0], reminder[reminder_type][str(reminder_id)][1] - 0.01), 2)
    to_timedelta = timedelta(hours=random_time)
    to_time = (datetime.min + to_timedelta).time()
    return to_time


def personal_greetings(nickname, language_code):
    try:
        now = datetime.now().time()
        now = int(now.strftime("%H"))
        if now < 11:
            greeting =ld.greetings["morning"][language_code]
        elif now < 18:
            greeting =ld.greetings["afternoon"][language_code]
        else:
            greeting = ld.greetings["evening"][language_code]
        if nickname:
            nickname = " " + nickname
        else:
            nickname = ""
        personal_greeting = greeting + nickname + "!"
        return personal_greeting
    except Exception as e:
        print (e)


def string_formatting(input_string):
    rx = r'(?<=[.,!?:])(?=[^\s])'
    s = input_string
    result = re.sub(rx, " ", s)
    return result


def convert_to_string(mylist):
    mylist = [str(i) for i in mylist]
    return mylist


#functions for dashboard
def moving_average(goal_list, n=3):
    ret = np.cumsum(goal_list, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


def achieved_goal(ls):
    x = sum(i[0] >= i[1] for i in ls)
    return x


def exceeding_goal(ls):
    x = sum(i[0] > i[1] for i in ls)
    return x


def difference_first_last(goal_list):
    goal_diff = goal_list[-1] - goal_list[0]
    return goal_diff


def difference_last_two(goal_list):
    goal_diff = goal_list[-1] - goal_list[-2]
    return goal_diff


def get_variability(achieved_list_var):
    del achieved_list_var[-1]
    x = np.linalg.norm(achieved_list_var)
    if int(x) == 0:
        pass
    else:
        normal_array = achieved_list_var / x
        diff_normal_array = sum([abs(normal_array[i] - normal_array[i + 1]) for i in range(0, len(normal_array) - 1, 1)])
        return diff_normal_array


def get_streak(streak_list):
    streak_list = streak_list[:-1]
    streak_list.reverse()
    no_streaks = 0
    for i in streak_list:
        if i[0] >= i[1]:
            no_streaks += 1
        else:
            break
    return no_streaks


def parse_hyperlink(text_to_parse, text_link_to_insert):
    def my_replace(match, var):
        print (match, var)
        return var + "(" + match.group() + ")"
    x = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    return re.sub(x, partial(my_replace, var=text_link_to_insert), text_to_parse)