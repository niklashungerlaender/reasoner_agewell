import _jsondicts as jd
import _helperfunctions as hf
import _databasefunctions as db
from durable.lang import *
from datetime import datetime, timedelta, date
import uuid
import _schedule
from _mqttconnection import publish_message
import _languagedicts as ld
from random import randint
import _sqlstatements as ss
import math
import numpy as np


# schedules notifications for weekly goals from ruleset firstgoal/intern and flowchart goal
def execute_scheduler_job(scheduler_event, client_id, scheduler_id=None, **kwargs):
    notification_id = uuid.uuid1().int
    language_code = db.DbQuery(ss.query("get_language", client_id=client_id), "query_one").create_thread()

    post(scheduler_event,
         {"sid": notification_id, "client_id": client_id, "scheduler_id": scheduler_id,
          "language_code": language_code, "kwargs": kwargs})


# receives button responses from notifications and sends them to ruleset
with ruleset('notification/response'):
    @when_all(+m.client_id)
    def post_to_ruleset(c):
        post(c.m.notification_name,
             {"sid": int(c.m.notification_id), "button_type": c.m.button_type,
              "questionnaire_answers": c.m.questionnaire_answers["ANSWERS"], "client_id": c.m.client_id,
              "language_code": c.m.language_code})

# ruleset which is triggered internally from preference/message when client_id is not yet in database.
# triggers scheduler job for ruleset firstgoal/intern
with ruleset('create/clientid/intern'):
    @when_all(+m.client_id)
    def create_user(c):
        try:
            db.DbQuery(ss.query("insert_clientid", client_id=c.m.client_id), "insert").create_thread()
            db.DbQuery(ss.query("update_language", client_id=c.m.client_id, language_code=c.m.language_code),
                       "insert").create_thread()
            post("firstgoal/intern", {"client_id": c.m.client_id, "language_code": c.m.language_code})
        except Exception as e:
            print(e)

# is triggered by ruleset clientid/message
with ruleset('firstgoal/intern'):
    @when_all(+m.client_id)
    def create_goal_notification(c):
        try:
            notification_id = str(uuid.uuid1().int)
            run_time = datetime.now() + timedelta(days=6)
            run_time = run_time.replace(hour=23, minute=59, second=59)
            db.DbQuery(ss.query("insert_goal", client_id=c.m.client_id, run_time=run_time), "insert").create_thread()
            _schedule.scheduler.add_job(execute_scheduler_job, id=notification_id + c.m.client_id,
                                        trigger="date", run_date=run_time,
                                        args=["goal", c.m.client_id])

            language_code = db.DbQuery(ss.query("get_language", client_id=c.m.client_id), "query_one").create_thread()
            query_content = db.DbQuery(ss.query("get_firstgoal_content", language_code=c.m.language_code),
                                       "query_all").create_thread()
            title = query_content[0][0]
            content = query_content[1][0]
            buttons = [hf.create_buttons_dict(button_type="ok", content="ok", language_code=language_code, wait=True)]
            topic = f"eu/agewell/event/reasoner/notification/message"
            message_dict = jd.create_notification_message(topic=topic, client_id=c.m.client_id,
                                                          title=title, content=content,
                                                          buttons=buttons,
                                                          language=language_code,
                                                          notification_name="ipaq/questionnaire",
                                                          notification_id=notification_id)
            print(message_dict)

            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# rulseset which is triggered by message from UI. Includes client ID and preferences
with ruleset('preference/message'):
    @when_all(+m.client_id)
    def insert_user_preferences(c):
        try:
            check_user_id = db.DbQuery(ss.query("get_language", client_id=c.m.client_id), "query_one").create_thread()
            if check_user_id:

                db.DbQuery(ss.query("update_user_info", client_id=c.m.client_id, language_code=c.m.language_code,
                                    age=c.m.preferences['userYearOfBirth'],
                                    nickname=c.m.preferences['userName'],
                                    morning_not=c.m.preferences['reminderTimeIndex'],
                                    evening_not=c.m.preferences['questionnaireTimeIndex'],
                                    gender=c.m.preferences['userGender']), "insert").create_thread()
                try:
                    update_notification_time = [(ss.query("update_notification", client_id=c.m.client_id,
                                                          notification_name="morning_notification"),
                                                 "morning", c.m.preferences['reminderTimeIndex']),
                                                (ss.query("update_notification", client_id=c.m.client_id,
                                                          notification_name="evening_notification"),
                                                 "evening", c.m.preferences['questionnaireTimeIndex'])]
                    for i in update_notification_time:
                        scheduler_ids = db.DbQuery(i[0], "query_all").create_thread()
                        hf.update_notification_time(scheduler_ids, i[1], i[2])

                except Exception as e:
                    print(e)
            else:
                post("create/clientid/intern", {"client_id": c.m.client_id, "language_code": c.m.language_code})

        except Exception as e:
            print(e)

with ruleset('user/activity/edit/request'):
    @when_all(m.dimension_id == 1)
    def get_activity_types(c):
        try:
            try:
                activity_types = db.DbQuery(ss.query("get_activity_types_edit", client_id=c.m.client_id,
                                                     activity_id=c.m.activity_id), "query_all").create_thread()
                selected_days = [i.weekday() for i in activity_types[0][2]]
                selected_duration = str(activity_types[0][3])
            except:
                activity_types = db.DbQuery(ss.query("get_activity_types_edit_except", client_id=c.m.client_id,
                                                     activity_id=c.m.activity_id), "query_all").create_thread()
                selected_days = []
                selected_duration = ""

            type_id = activity_types[0][0]
            duration = activity_types[0][1]
            duration = hf.convert_to_string(duration)
            # check if task for today already done
            activity_done_today = db.DbQuery(ss.query("get_task_done", client_id=c.m.client_id,
                                                      activity_id=c.m.activity_id), "query_one").create_thread()
            print(activity_done_today)
            end_date = db.DbQuery(ss.query("get_goal_enddate", client_id=c.m.client_id), "query_one").create_thread()
            start_date = datetime.now()
            days_activity = []
            if end_date is not None:
                for dt in hf.daterange(start_date, end_date):
                    days_activity.append({"ID": datetime.weekday(dt),
                                          "CONTENT_DISPLAY": ld.weekDays[c.m.language_code][datetime.weekday(dt)]})
            print(days_activity)
            # if task for today is done deselect it
            if activity_done_today is not None:
                days_activity = [i for n, i in enumerate(days_activity) if
                                 i["ID"] not in [datetime.weekday(date.today())]]
            print(days_activity)
            content_sub_screens = [("activity_days", "", ld.text_to_speech["days_edit"][c.m.language_code]),
                                   ("activity_duration", "", ld.text_to_speech["duration"][c.m.language_code])]
            topic = "eu/agewell/event/reasoner/user/activity/edit/response"
            message_dict = jd.create_activity_types_edit_response(topic=topic, client_id=c.m.client_id,
                                                                  days=days_activity, selected_days=selected_days,
                                                                  selected_duration=selected_duration,
                                                                  activity_id=type_id,
                                                                  language=c.m.language_code, duration=duration,
                                                                  content_display_sub_screens=content_sub_screens)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# ruleset which returns actìvities which are currently not chosen by the user. Includes time, day and info
with ruleset('activitytypes/request'):
    @when_all(m.dimension_id == 1)
    def get_activity_types(c):
        try:
            activity_types = db.DbQuery(ss.query("get_activity_types", client_id=c.m.client_id,
                                                 language_code=c.m.language_code), "query_all").create_thread()
            start_date = datetime.now()
            end_date = db.DbQuery(ss.query("get_goal_enddate", client_id=c.m.client_id), "query_one").create_thread()
            days_activity = []
            if end_date is not None:
                for dt in hf.daterange(start_date, end_date):
                    days_activity.append({"ID": datetime.weekday(dt),
                                          "CONTENT_DISPLAY": ld.weekDays[c.m.language_code][datetime.weekday(dt)]})
            days_activity = [i for n, i in enumerate(days_activity) if i not in days_activity[n + 1:]]
            content_sub_screens = [("activity_type", "", ld.text_to_speech["select_activity"][c.m.language_code]),
                                   ("activity_days", "", ld.text_to_speech["days"][c.m.language_code]),
                                   ("activity_duration", "", ld.text_to_speech["duration"][c.m.language_code])]

            topic = "eu/agewell/event/reasoner/activitytypes/response"
            message_dict = jd.create_activity_types_response(topic=topic, client_id=c.m.client_id,
                                                             types=activity_types, days=days_activity,
                                                             language=c.m.language_code,
                                                             content_display_sub_screens=content_sub_screens)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# ruleset which creates a message to show the met value of the current choice as well as left weekly mets after the
# choice
with ruleset('creditsinformation/request'):
    @when_all(m.dimension_id == 1)
    def insert_user_preferences(c):
        try:
            met_value = db.DbQuery(ss.query("get_met_value", activity_id=c.m.activity_id), "query_one").create_thread()
            try:
                met_calculation = met_value * int(c.m.selected_duration) * len(c.m.selected_days)
            except Exception as e:
                print(e)
                met_calculation = 0
            message_constellation_general = db.DbQuery(ss.query("get_content", purpose="credits_information_general",
                                                                language_code=c.m.language_code),
                                                       "query_one").create_thread()
            message_constellation_general = message_constellation_general.format(met_calculation)
            weekly_goal_mets = db.DbQuery(ss.query("get_weekly_mets", client_id=c.m.client_id),
                                          "query_one").create_thread()
            if weekly_goal_mets is None:
                weekly_goal_mets = 0

            active_mets = db.DbQuery(ss.query("get_active_mets", client_id=c.m.client_id,
                                              activity_id=c.m.activity_id), "query_all").create_thread()
            active_mets = sum(i[0] * i[1] for i in active_mets)
            left_mets = weekly_goal_mets - (met_calculation + active_mets)
            if left_mets > 50:
                scnd_msg = "credits_information_more"
                mets_msg = left_mets
            elif left_mets < -50:
                scnd_msg = "credits_information_less"
                mets_msg = abs(left_mets)
            else:
                scnd_msg = "credits_information_stay"

            message_constellation_specific = db.DbQuery(ss.query("get_content",
                                                                 language_code=c.m.language_code,
                                                                 purpose=scnd_msg), "query_one").create_thread()
            if scnd_msg != "credits_information_stay":
                message_constellation_specific = message_constellation_specific.format(mets_msg)

            topic = "eu/agewell/event/reasoner/creditsinformation/response"
            text = message_constellation_general + message_constellation_specific
            message_dict = jd.create_credits_information_response(topic=topic, client_id=c.m.client_id,
                                                                  text=text, language=c.m.language_code)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# inserts the chosen activity into the database and sets deselected choices to inactive
with ruleset('user/activity/message'):
    @when_all(m.dimension_id == 1)
    def insert_user_activity(c):
        try:
            db.DbQuery(ss.query("insert_activity", client_id=c.m.client_id, activity_id=c.m.activity_id),
                       "insert").create_thread()

            dates_for_tasks = []
            reminder_id_morning = db.DbQuery(ss.query("get_morning_not_id", client_id=c.m.client_id),
                                             "query_one").create_thread()
            reminder_id_evening = db.DbQuery(ss.query("get_evening_not_id", client_id=c.m.client_id),
                                             "query_one").create_thread()
            if reminder_id_morning is None:
                reminder_id_morning = 0
            if reminder_id_evening is None:
                reminder_id_evening = 0
            try:
                test_if_emty = c.m.selected_days[0]
                start_date = db.DbQuery(ss.query("get_goal_startdate", client_id=c.m.client_id),
                                        "query_one").create_thread()
                end_date = db.DbQuery(ss.query("get_goal_enddate", client_id=c.m.client_id),
                                      "query_one").create_thread()
                for day in c.m.selected_days:
                    day = int(day)
                    date_for_task = datetime(1900, 1, 1)
                    for dt in hf.daterange(start_date, end_date):
                        if dt.weekday() == day:
                            date_for_task = dt
                        else:
                            pass
                    date_for_scheduler = date_for_task
                    date_for_task = datetime.strftime(date_for_task, '%Y-%m-%d')
                    dates_for_tasks.append(date_for_task)
                    task_id = db.DbQuery(ss.query("insert_task", client_id=c.m.client_id, activity_id=c.m.activity_id,
                                                  duration=c.m.selected_duration, date_task=date_for_task),
                                         "insert").create_thread()

                    scheduler_id_morning = c.m.client_id + str(c.m.activity_id) + str(day) + "morning_notification"
                    scheduler_id_evening = c.m.client_id + str(c.m.activity_id) + str(day) + "evening_notification"

                    _schedule.CreateSchedulerJob(date_for_scheduler, c.m.client_id, reminder_id=reminder_id_morning,
                                                 scheduler_id=scheduler_id_morning,
                                                 activity_type=c.m.activity_id,
                                                 duration=int(c.m.selected_duration),
                                                 weekday=day, task_id=task_id).morning_notification()

                    _schedule.CreateSchedulerJob(date_for_scheduler, c.m.client_id, reminder_id=reminder_id_evening,
                                                 scheduler_id=scheduler_id_evening,
                                                 activity_type=c.m.activity_id, task_id=task_id,
                                                 weekday=day).evening_notification()

            except IndexError:
                pass

            if len(dates_for_tasks) > 1:
                to_update = "update_task"
            elif len(dates_for_tasks) == 1:
                dates_for_tasks = dates_for_tasks[0]
                to_update = "update_task_ifone"
            else:
                to_update = "update_task_ifzero"
            db.DbQuery(ss.query(to_update, client_id=c.m.client_id, activity_id=c.m.activity_id,
                                date_task=dates_for_tasks), "insert").create_thread()
            topic = "eu/agewell/event/reasoner/user/activity/response"
            message_dict = jd.create_useractivity_response(topic=topic, client_id=c.m.client_id,
                                                           activity_id=c.m.activity_id)
            print(message_dict)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# provides a short overview of the weekly progress with text and percentage done
with ruleset('dimension/request'):
    @when_all(+m.client_id)
    def get_dimension_info(c):
        try:
            content = db.DbQuery(ss.query("get_dimension_request_content", language_code=c.m.language_code),
                                 "query_all").create_thread()
            weekly_goal_mets = db.DbQuery(ss.query("get_weekly_mets", client_id=c.m.client_id),
                                          "query_one").create_thread()
            if weekly_goal_mets is None:
                weekly_goal_mets = 0

            done_mets = db.DbQuery(ss.query("get_done_mets", client_id=c.m.client_id), "query_all").create_thread()
            done_mets = sum(i[0] * i[1] for i in done_mets)

            try:
                done_mets_percentage = int(done_mets * 100 / weekly_goal_mets)
            except Exception as e:
                print(e)
                done_mets_percentage = 0
            dashboard_content = content[1][0].format(done_mets_percentage)

            if done_mets_percentage >= 75:
                scnd_msg = "dashboard_content_pos"
            elif done_mets_percentage <= 25:
                scnd_msg = "dashboard_content_neg"
            else:
                scnd_msg = "dashboard_content_neu"

            dashboard_motivation = db.DbQuery(ss.query("get_content", purpose=scnd_msg,
                                                       language_code=c.m.language_code), "query_one").create_thread()

            topic = "eu/agewell/event/reasoner/dimension/response"
            title = content[0][0]
            title_short = "Physical"
            text = dashboard_motivation + dashboard_content
            message_dict = jd.create_dimension_notification(topic=topic, client_id=c.m.client_id,
                                                            title=title, title_short=title_short,
                                                            text=text, progress=done_mets_percentage,
                                                            language=c.m.language_code)
            print(message_dict)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

#
with ruleset('user/activities/request'):
    @when_all(m.dimension_id == 1)
    def get_user_activities(c):
        try:
            active_goal = db.DbQuery(ss.query("get_goal_id", client_id=c.m.client_id), "query_one").create_thread()
            #checks if there is a goal, if not one is created with 1000 credits
            if not active_goal:
                notification_id = str(uuid.uuid1().int)
                run_time = datetime.now() + timedelta(days=6)
                run_time = run_time.replace(hour=23, minute=59, second=59)
                db.DbQuery(ss.query("insert_goal", client_id=c.m.client_id, run_time=run_time),
                           "insert").create_thread()
                _schedule.scheduler.add_job(execute_scheduler_job, id=notification_id + c.m.client_id,
                                            trigger="date", run_date=run_time,
                                            args=["goal", c.m.client_id])

            #query variables
            weekly_goal_mets = db.DbQuery(ss.query("get_weekly_mets", client_id=c.m.client_id),
                                          "query_one").create_thread()
            allocated_mets = db.DbQuery(ss.query("get_selected_mets", client_id=c.m.client_id),
                                        "query_all").create_thread()
            done_mets = db.DbQuery(ss.query("get_done_mets", client_id=c.m.client_id), "query_all").create_thread()
            content_goalinfo = db.DbQuery(ss.query("get_goalinfo_content", language_code=c.m.language_code),
                                          "query_all").create_thread()
            activity_infos = db.DbQuery(ss.query("get_activity_infos", client_id=c.m.client_id),
                                        "query_all").create_thread()
            nickname = db.DbQuery(ss.query("get_nickname", client_id=c.m.client_id), "query_one").create_thread()
            goal_start_date = db.DbQuery(ss.query("get_goal_startdate", client_id=c.m.client_id),
                                         "query_one").create_thread()
            goal_end_date = db.DbQuery(ss.query("get_goal_enddate", client_id=c.m.client_id),
                                       "query_one").create_thread()
            number_of_weeks_participating = db.DbQuery(ss.query("get_number_of_weeks", client_id=c.m.client_id),
                                                       "query_one").create_thread()
            gender = db.DbQuery(ss.query("get_gender", client_id=c.m.client_id), "query_one").create_thread()

            #compute queried variables
            if weekly_goal_mets == None:
                weekly_goal_mets = 0
            try:
                allocated_mets = sum(i[0] * i[1] for i in allocated_mets)
                left_mets = weekly_goal_mets - allocated_mets
            except:
                allocated_mets = 0
                left_mets = weekly_goal_mets

            done_mets = sum(i[0] * i[1] for i in done_mets)

            goalinfo_info = content_goalinfo[0][0].format(weekly_goal_mets)
            goalinfo_achieved = content_goalinfo[1][0].format(allocated_mets)
            if left_mets > 0:
                goalinfo_remaining = content_goalinfo[2][0].format(left_mets)
            else:
                goalinfo_remaining = ""

            goalinfo_activities = content_goalinfo[3][0]
            goalinfo_1 = goalinfo_info + goalinfo_achieved + goalinfo_remaining + goalinfo_activities

            try:
                activity_active_today = db.DbQuery(ss.query("get_activities_active_today", client_id=c.m.client_id),
                                                   "query_all").create_thread()
                activity_active_today = [var for tup in activity_active_today for var in tup]
            except:
                activity_active_today = []
            try:
                activity_done_today = db.DbQuery(ss.query("get_activities_done_today", client_id=c.m.client_id),
                                                   "query_all").create_thread()
            except:
                activity_done_today = []
            activity_missed = db.DbQuery(ss.query("get_missed_days", client_id=c.m.client_id),
                                         "query_all").create_thread()
            activity_missed = [var for tup in activity_missed for var in tup]
            if len(activity_missed) > 0:
                post("activity/missed", {"client_id":c.m.client_id, "language_code":c.m.language_code, "nickname":nickname})
                db.DbQuery(ss.query("delete_missed_days", client_id=c.m.client_id),
                                                 "insert").create_thread()
            activity_infos = [
                {"activity_name": ld.activity_name[i[0]][c.m.language_code],
                 "days": [ld.weekDays[c.m.language_code][j.weekday()] for j in i[1]], "activity_duration": i[2],
                 "activities_done": i[3], "met_value": i[4], "type_id": i[5], "url": i[6],
                 "activity_name_english": i[0],
                 "active_today": True if i[0] in activity_active_today else False,
                 "text_to_speech": ld.text_to_speech["activity_today"][c.m.language_code]
                 if i[0] in activity_active_today
                 else ld.text_to_speech["delete_info"][c.m.language_code] if i[0] in activity_missed
                 else ld.text_to_speech["activity_info"][c.m.language_code],
                 "keyword": hf.get_hyphenation(ld.activity_name[i[0]][c.m.language_code], c.m.language_code)}
                for i in activity_infos
            ]
            goal_text = goalinfo_1

            goalinfo_text = db.DbQuery(ss.query("get_goalinfo_content_specific", language_code=c.m.language_code),
                                       "query_all").create_thread()

            if len(activity_infos) == 0:
                activity_content = ""
            elif len(activity_infos) == 1:
                activities = activity_infos[0]["activity_name_english"]
                sql_statement = (
                    f"Select activity, ARRAY_AGG(content{c.m.language_code}) as content, ARRAY_AGG(category) as "
                    f"category "
                    f"FROM template WHERE activity IN ('{activities}') GROUP BY activity ")
                activity_content = db.DbQuery(sql_statement, "query_all").create_thread()
            else:
                activities = tuple(sub["activity_name_english"] for sub in activity_infos)
                sql_statement = (
                    f"Select activity, ARRAY_AGG(content{c.m.language_code}) as content, ARRAY_AGG(category) as "
                    f"category "
                    f"FROM template WHERE activity IN {activities} GROUP BY activity ")

                activity_content = db.DbQuery(sql_statement, "query_all").create_thread()
            activity_list = []
            for h, i in enumerate(activity_infos):
                # i["days"].reverse()
                goalinfo_days = goalinfo_text[0][0].format(i["activity_name"].capitalize(),
                                                           (' ' + ld.and_name[c.m.language_code] + ' ').join(i["days"]),
                                                           i["activity_duration"])
                goalinfo_info = goalinfo_text[1][0].format(i["activity_duration"] * i["met_value"] * len(i["days"]))
                if i["activities_done"] == count(i["days"]):
                    goalinfo_extra = goalinfo_text[3][0]
                elif i["activities_done"] == 0:
                    goalinfo_extra = ""
                else:
                    goalinfo_extra = goalinfo_text[2][0].format(
                        i["activity_duration"] * i["met_value"] * i["activities_done"])

                goal_text += goalinfo_days + goalinfo_info + goalinfo_extra
                index_for_activity = [x for x, y in enumerate(activity_content) if
                                      y[0] == i["activity_name_english"]][0]
                random_content = randint(0, len(activity_content[index_for_activity][2]) - 1)
                dict_for_activity = {"ID": i["type_id"], "TITLE_DISPLAY": i["activity_name"],
                                     "CREDIT_SCORE": i["activity_duration"] * i["met_value"] * len(i["days"]),
                                     "CREDIT_DONE": i["activity_duration"] * i["met_value"] * i["activities_done"],
                                     "CONTENT_DISPLAY": (': '.join(
                                         ("**" +
                                          ld.content_title[
                                              activity_content[index_for_activity][2]
                                              [random_content]][c.m.language_code] + "**",
                                          activity_content[index_for_activity][1]
                                          [random_content]))),
                                     "CONTENT_TEXT_TO_SPEECH": i["text_to_speech"],
                                     "CONTENT_IMAGE": i["url"],
                                     "ACTIVE_TODAY": i["active_today"],
                                     "KEYWORD": i["keyword"]
                                     }
                activity_list.append(dict_for_activity)


            if gender is "FEMALE":
                gender = "female"
            else:
                gender = "male"
            if nickname:
                nickname = " " + nickname
            else:
                nickname = ""

            if allocated_mets == 0 and number_of_weeks_participating == 1:
                text_to_speech_main = ld.text_to_speech["first_week"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["first_week"][c.m.language_code].format(
                    ld.italian_gender["new_week"][gender])
            elif allocated_mets == 0 and goal_start_date.date() == date.today():
                text_to_speech_main = ld.text_to_speech["new_week"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["new_week"][c.m.language_code].format(
                    ld.italian_gender["new_week"][gender])
            elif allocated_mets == 0:
                text_to_speech_main = ld.text_to_speech["allocate_mets_zero"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["allocate_credits"][c.m.language_code] + str(left_mets)
            elif left_mets > 0:
                text_to_speech_main = ld.text_to_speech["allocate_mets"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["allocate_credits"][c.m.language_code] + str(left_mets)
            elif len(activity_active_today) == 1:
                text_to_speech_main = ld.text_to_speech["activity_today_single"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["activity_today_single"][c.m.language_code] + str(
                    list(map(lambda x: ld.activity_name[x][c.m.language_code], activity_active_today))[0])
            elif activity_active_today:
                text_to_speech_main = ld.text_to_speech["activity_today_multiple"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["activity_today_multiple"][c.m.language_code] \
                                + ", ".join(
                    list(map(lambda x: ld.activity_name[x][c.m.language_code], activity_active_today)))

            elif len(activity_done_today) > 0:
                text_to_speech_main = ld.text_to_speech["on_track"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["weekly_credits"][c.m.language_code].format(done_mets,
                                                                                                 allocated_mets,
                                                                                                 weekly_goal_mets)
            else:
                text_to_speech_main = ld.text_to_speech["day_off"][c.m.language_code].format(nickname)
                title_display = ld.title_goal_screen["weekly_credits"][c.m.language_code].format(done_mets,
                                                                                                 allocated_mets,
                                                                                                 weekly_goal_mets)

            text_to_speech_sub = ld.text_to_speech["goal_info"][c.m.language_code]
            start_day = ld.weekDays[c.m.language_code][datetime.weekday(goal_start_date)]
            end_day = ld.weekDays[c.m.language_code][datetime.weekday(goal_end_date)]
            days_left = (goal_end_date - datetime.today()).days + 1
            title_display_sub = ld.title_goal_screen["personal_week"][c.m.language_code].format(start_day, end_day,
                                                                                                days_left)
            topic = "eu/agewell/event/reasoner/user/activities/response"
            message_dict = jd.create_user_activity_response(topic=topic, client_id=c.m.client_id,
                                                            goal_credits=weekly_goal_mets,
                                                            content_display_sub=goal_text,
                                                            activities_list=activity_list,
                                                            language=c.m.language_code,
                                                            title_display=title_display,
                                                            text_to_speech_sub=text_to_speech_sub,
                                                            text_to_speech_main=text_to_speech_main,
                                                            title_display_sub=title_display_sub)

            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

with ruleset('user/dashboard/request'):
    @when_all(+m.client_id)
    def create_dashboard_response(c):
        try:
            chart_type = "COMBINED"
            title_display = ld.activity_name["activity"][c.m.language_code]
            legend = [ld.dashboard["achieved"][c.m.language_code],ld.dashboard["goal"][c.m.language_code]]
            sql_statement = f"SELECT count(goal_id) from goal WHERE user_id = '{c.m.client_id}'"
            number_of_weeks = db.DbQuery(sql_statement, "query_one").create_thread()
            number_of_weeks = max(0, number_of_weeks-5)
            sql_statement = (f"SELECT achieved, met_required from goal where user_id = '{c.m.client_id}' "
                             f"ORDER BY goal_id DESC LIMIT 5")
            goal_vars = db.DbQuery(sql_statement, "query_all").create_thread()
            goal_vars = [list(ele) for ele in goal_vars]
            goal_vars.reverse()
            done_mets = db.DbQuery(ss.query("get_done_mets", client_id=c.m.client_id), "query_all").create_thread()
            done_mets = sum(i[0] * i[1] for i in done_mets)
            data = []
            for i, j in enumerate(goal_vars):
                x = {"X": ld.dashboard["week"][c.m.language_code] + " " + str(i + 1 + number_of_weeks),
                     "Y": [0 if v is None else v for v in j]}
                data.append(x)
            data[-1]["Y"][0] = done_mets
            #get plot description (ruleset at end of script)
            post('dashboard', {'sid': c.m.client_id, 'input': list(data[i]["Y"] for i in range(len(data))), 'language': c.m.language_code})
            content_display = hf.StoreInput(c.m.client_id, "dashboard").get_value()
            hf.StoreInput(c.m.client_id, "dashboard").delete_entry()

            topic = "eu/agewell/event/reasoner/user/dashboard/response"
            message_dict = jd.create_dashboard_response(topic=topic, client_id=c.m.client_id,
                                                        language=c.m.language_code,
                                                        type=chart_type, content_display=content_display,
                                                        title_display=title_display, legend=legend, data=data)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print (e)

with ruleset('delete/user'):
    @when_all(+m.client_id)
    def get_user_activities(c):
        sql_statement = f" DELETE from apscheduler_jobs where id LIKE '{c.m.client_id}' + '%'"
        db.DbQuery(sql_statement, "insert").create_thread()
        sql_statement = f" DELETE from apscheduler_jobs where id LIKE '%' + '{c.m.client_id}'"
        db.DbQuery(sql_statement, "insert").create_thread()
        sql_statement = f" DELETE from user_info where id = '{c.m.client_id}'"
        db.DbQuery(sql_statement, "insert").create_thread()

# manually finish task
with ruleset('user/activities/status/message'):
    @when_all(m.dimension_id == 1)
    def finish_task(c):
        sid = uuid.uuid1().int
        task_id = db.DbQuery(ss.query("get_task_id", client_id=c.m.client_id, activity_id=c.m.activity_id),
                             "query_one").create_thread()
        post("notification/evening", {"sid": sid, "client_id": c.m.client_id, "language_code": c.m.language_code,
                                      "activity_type": c.m.activity_id, "task_id": task_id, "user_input": True})

with flowchart("goal"):
    # calculate percentage of goal done and adjust the new goal dependent
    # on the credits of the old goal
    with stage("input"):
        to('info').when_all(+m.client_id)

    with stage('info'):
        @run
        def create_goal_notification(c):
            try:
                notification_id = str(uuid.uuid1().int)
                sql_statement = (f"SELECT goal_id, met_required, end_date from goal where user_id = '{c.m.client_id}' "
                                 f"ORDER BY goal_id DESC LIMIT 1")
                goal_vars = db.DbQuery(sql_statement, "query_all").create_thread()
                goal_id = goal_vars[0][0]
                goal_mets = goal_vars[0][1]
                end_date = goal_vars[0][2]
                run_time = end_date + timedelta(days=7)
                run_time = run_time.replace(hour=23, minute=59, second=59)
                _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", id=notification_id + c.m.client_id,
                                            run_date=run_time,
                                            args=["goal", c.m.client_id])
                sql_statement = (f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                                 f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                                 f"activity.activity_id WHERE a.active='True' and a.activity_done='True'"
                                 f"and a.activity_id IN (SELECT m.activity_id from activity m WHERE "
                                 f"m.goal_id = {goal_id})")
                done_mets = db.DbQuery(sql_statement, "query_all").create_thread()
                done_mets = sum(i[0] * i[1] for i in done_mets)
                try:
                    percentage_done_mets = int(done_mets * 100 / goal_mets)
                except Exception as e:
                    print(e)
                    percentage_done_mets = 0

                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{notification_goal_title, notification_goal_content, 
                                 notification_goal_stay,notification_goal_newgoal, increase, decrease}'::TEXT[]) 
                                 WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")

                query_content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = query_content[0][0]
                content_1 = query_content[1][0].format(percentage_done_mets)

                if 75 >= percentage_done_mets >= 70:
                    new_goal = goal_mets
                    content_2 = query_content[2][0]
                else:
                    if percentage_done_mets > 75:
                        increase_decrease_mets = int((percentage_done_mets - 75) * 100 / math.log(goal_mets))
                        new_goal = goal_mets + increase_decrease_mets
                        increase_decrease = query_content[4][0]
                    else:  # if percentage_done_mets < 70:
                        increase_decrease_mets = int(goal_mets / 50 * (-0.333 * percentage_done_mets + 25))
                        new_goal = goal_mets - increase_decrease_mets
                        increase_decrease = query_content[5][0]
                    new_goal = round(new_goal, -1)
                    if new_goal < 100:
                        new_goal = 100
                    content_2 = query_content[3][0].format(increase_decrease, increase_decrease_mets, new_goal)
                content = content_1 + content_2

                hf.StoreInput(c.m.sid, "new_weekly_goal", new_goal).add_value()

                sql_statement = (f"INSERT INTO goal(user_id, start_date, end_date, met_required, achieved) VALUES "
                                 f"('{c.m.client_id}','{end_date + timedelta(seconds=1)}' "
                                 f",'{run_time}', {new_goal}, {done_mets})")
                db.DbQuery(sql_statement, "insert").create_thread()

                button_left = hf.create_buttons_dict(button_type="edit", content="edit",
                                                     language_code=c.m.language_code, wait=True)
                button_right = hf.create_buttons_dict(button_type="ok", content="ok",
                                                      language_code=c.m.language_code)
                buttons = [button_right, button_left]
                s.topic = "eu/agewell/event/reasoner/notification/message"
                s.notification_name = "goal"
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              title=title, content=content, buttons=buttons,
                                                              notification_id=c.m.sid,
                                                              notification_name=s.notification_name)

                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('adjustment').when_all(m.button_type == "edit")

    with stage('adjustment'):
        @run
        def create_adjustment_goal_notification(c):
            try:
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{goalprogress_adjustment_title, 
                                 goalprogress_adjustment_content,goalprogress_adjustment_increase,
                                 goalprogress_adjustment_decrease, goalprogress_adjustment_stay }'::TEXT[])
                                 WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                query_content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = query_content[0][0]
                content = query_content[1][0]
                increase_question = query_content[2][0]
                decrease_question = query_content[3][0]
                maintain_question = query_content[4][0]
                new_weekly_goal = hf.StoreInput(c.m.sid, "new_weekly_goal").get_value()
                increase_decrease_values = {"1": 100, "2": 300, "3": new_weekly_goal, "4": 100, "5": 300}
                increase_decrease_text = [increase_question.format(increase_decrease_values["1"]),
                                          increase_question.format(increase_decrease_values["2"]),
                                          maintain_question.format(increase_decrease_values["3"]),
                                          decrease_question.format(increase_decrease_values["4"]),
                                          decrease_question.format(increase_decrease_values["5"])]
                item_list = [hf.create_items_dict(
                    item_type="single_radio", item_id=1,
                    options=[str(i) for i in increase_decrease_text])
                ]
                questions = hf.create_question_dict(content_display=[""], items=[item_list])
                buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                                  language_code=c.m.language_code)]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              title=title, content=content, buttons=buttons,
                                                              notification_id=c.m.sid, questions=questions,
                                                              notification_name=s.notification_name)
                print(message_dict)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('update_goal').when_all(m.button_type == "ok")

    with stage('update_goal'):
        @run
        def update_goal(c):
            new_weekly_goal = hf.StoreInput(c.m.sid, "new_weekly_goal").get_value()
            increase_decrease_values = {"1": 100, "2": 300, "3": new_weekly_goal, "4": 100, "5": 300}
            try:
                if new_weekly_goal > 100:
                    question_id = c.m.questionnaire_answers[0]["ITEMS"][0]["SELECTED_OPTION_IDS"][0]
                    if question_id == 1 or question_id == 2:
                        updated_goal = new_weekly_goal + increase_decrease_values[str(question_id)]
                    elif question_id == 4 or question_id == 5:
                        updated_goal = new_weekly_goal - increase_decrease_values[str(question_id)]
                    else:
                        updated_goal = new_weekly_goal

                    sql_statement = (f"UPDATE goal SET met_required = {updated_goal} "
                                     f"WHERE user_id = '{c.m.client_id}' and CURRENT_TIMESTAMP between "
                                     f"start_date and end_date")
                    print(sql_statement)
                    db.DbQuery(sql_statement, "insert").create_thread()
                else:
                    pass
                hf.StoreInput(c.m.sid).delete_entry()
                c.delete_state()
            except Exception as e:
                print(e)

with ruleset('notification/morning'):
    @when_all(+m.scheduler_id)
    def get_activity_name(c):
        try:
            hf.StoreInput(c.m.sid, "task_id", c.m.kwargs['task_id']).add_value()
            s.client_id = c.m.client_id
            s.kwargs = c.m.kwargs
            s.sid = c.m.sid
            s.language_code = c.m.language_code
            sql_statement = f"Select activity_name FROM activity_type WHERE type_id = {c.m.kwargs['activity_type']}"
            s.activity_name_english = db.DbQuery(sql_statement, "query_one").create_thread()
            s.activity_name = ld.activity_name[s.activity_name_english][c.m.language_code]
            print(s.activity_name)
            c.post({"get_last_session": True})
        except Exception as e:
            print(e)


    @when_all(+m.get_last_session)
    def get_last_session(c):
        try:
            sql_statement = (f"Select feedback FROM task WHERE activity_id IN (SELECT activity_id from "
                             f"activity where user_id = '{s.client_id}' and type_id = {s.kwargs['activity_type']}) "
                             f" and task_id != {s.kwargs['task_id']} and start_daytime < CURRENT_TIMESTAMP "
                             f" ORDER BY start_daytime DESC LIMIT 1")
            last_session_value = db.DbQuery(sql_statement, "query_one").create_thread()
            print(last_session_value)
            if last_session_value is None:
                last_session_value = "nan"
            c.post({"last_session": last_session_value})
        except Exception as e:
            print(e)


    @when_all(m.last_session == "nan")
    def get_value_session(c):
        c.post({"value_session": "dq"})


    @when_all(m.last_session == "easy")
    def get_value_session(c):
        c.post({"value_session": "ib"})


    @when_all(m.last_session == "dislike")
    def get_value_session(c):
        c.post({"value_session": "db"})


    @when_all(m.last_session == "like")
    def get_value_session(c):
        c.post({"value_session": "mb"})


    @when_all(+m.value_session)
    def get_message(c):
        try:
            sql_queries = [(
                f"SELECT m.content{s.language_code}, m.template_id from template m where m.daily = '{c.m.value_session}' "
                f"and NOT EXISTS(SELECT FROM message a WHERE m.template_id = a.template_id AND "
                f"EXISTS(SELECT from notification s WHERE a.notification_id = s.notification_id and "
                f"s.user_id = '{s.client_id}'))"),
                (
                    f"SELECT template.content{s.language_code}, template.template_id FROM message INNER JOIN template "
                    f"ON message.template_id = "
                    f"template.template_id INNER JOIN notification ON notification.notification_id = "
                    f"message.notification_id WHERE notification.user_id = '{s.client_id}' and notification.rating = 1"),
                (
                    f"select content{s.language_code}, template_id from template where daily = '{c.m.value_session}'")]

            s.content_msg = db.ChooseMessage(sql_queries, s.sid, s.client_id).choose_right_message()
            print(s.content_msg[1])
        except Exception as e:
            print(e)
        c.post({"credit_message": True})


    @when_all(+m.credit_message)
    def get_message(c):
        sql_statement = (f"SELECT met_required from goal where CURRENT_TIMESTAMP between start_date "
                         f"and end_date and user_id = '{s.client_id}'")
        goal_credits = db.DbQuery(sql_statement, "query_one").create_thread()
        sql_statement = f"SELECT met_value from activity_type where type_id = {s.kwargs['activity_type']}"
        met_value = db.DbQuery(sql_statement, "query_one").create_thread()
        try:
            s.percentage_of_credits = int((met_value * s.kwargs["duration"]) * 100 / goal_credits)
        except Exception as e:
            print(e)
            s.percentage_of_credits = 0
        c.post({"create_notification_message": True})


    @when_all(+m.create_notification_message)
    def send_message(c):
        try:
            sql_statement = (f"Select content{s.language_code} FROM template JOIN "
                             """unnest('{notification_morning_credits, 
                             notification_morning_title, notification_morning_activity}'::TEXT[])
                             WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
            met_message = query_content[0][0].format(s.percentage_of_credits)

            nickname = db.DbQuery(ss.query("get_nickname", client_id=s.client_id), "query_one").create_thread()
            personal_greeting = hf.personal_greetings(nickname, s.language_code)
            title = personal_greeting + query_content[1][0]
            activity_name_message = query_content[2][0].format(s.activity_name, s.kwargs["duration"])
            print(activity_name_message, s.content_msg, met_message)
            content = activity_name_message + s.content_msg + met_message

            button_left = hf.create_buttons_dict(button_type="cancel", content="ignore", language_code=s.language_code)
            button_right = hf.create_buttons_dict(button_type="ok", content="thanks", language_code=s.language_code)
            button_middle = hf.create_buttons_dict(button_type="postpone", content="postpone",
                                                   language_code=s.language_code)
            buttons = [button_right, button_left, button_middle]
            topic = f"eu/agewell/event/reasoner/notification/message"
            notification_name = "notification/morning"
            message_dict = jd.create_notification_message(topic=topic, client_id=s.client_id, notification_id=s.sid,
                                                          title=title, content=content,
                                                          buttons=buttons,
                                                          language=s.language_code,
                                                          notification_name=notification_name)
            publish_message(s.client_id, topic, message_dict)
        except Exception as e:
            print(e)


    @when_all(m.button_type == "ok")
    def get_feedback(c):
        sql_statement = (f"UPDATE notification SET rating = 1"
                         f"WHERE notification_id = '{c.m.sid}'")
        db.DbQuery(sql_statement, "insert").create_thread()
        c.delete_state()


    @when_all(m.button_type == "cancel")
    def get_feedback(c):
        sql_statement = (f"UPDATE notification SET rating = 2"
                         f"WHERE notification_id = '{c.m.sid}'")
        db.DbQuery(sql_statement, "insert").create_thread()
        c.delete_state()


    @when_all(m.button_type == "postpone")
    def get_feedback(c):
        try:
            task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
            sql_statement = (f"UPDATE notification SET rating = 3"
                             f"WHERE notification_id = '{c.m.sid}'")
            db.DbQuery(sql_statement, "insert").create_thread()
            scheduler_id_morning = s.client_id + str(s.activity_name_english) + str(datetime.weekday(date.today())) + \
                                   "morning_notification "
            date_for_scheduler = datetime.now() + timedelta(hours=randint(1, 3))
            _schedule.CreateSchedulerJob(date_for_scheduler, s.client_id, task_id=task_id,
                                         scheduler_id=scheduler_id_morning,
                                         activity_type=s.kwargs['activity_type'], postpone_time="notification/morning",
                                         duration=int(s.kwargs["duration"]),
                                         weekday=datetime.weekday(date.today())).postpone()
            c.delete_state()
        except Exception as e:
            print(e)

with flowchart('notification/evening'):
    with stage("input"):
        to('first_message').when_all(+m.scheduler_id)
        to('manual').when_all(+m.user_input)

    with stage('manual'):
        @run
        def define_variables(c):
            try:
                s.topic = "eu/agewell/event/reasoner/notification/message"
                s.notification_name = "notification/evening"
                hf.StoreInput(c.m.sid, "task_id", c.m.task_id).add_value()
                hf.StoreInput(c.m.sid, "activity_type", c.m.activity_type).add_value()
                hf.StoreInput(c.m.sid, "client_id", c.m.client_id).add_value()
                hf.StoreInput(c.m.sid, "language_code", c.m.language_code).add_value()
                sql_statement = (f"INSERT INTO notification(notification_id, user_id, timestamp, rating) VALUES "
                                 f"({c.m.sid},'{c.m.client_id}','{datetime.now()}', 0)")
                db.DbQuery(sql_statement, "insert").create_thread()
                post('notification/evening', {"sid": c.m.sid, "to_ask_time": "ok"})
            except Exception as e:
                print (e)

        to('ask_time').when_all(m.to_ask_time == 'ok')

    with stage('first_message'):
        @run
        def create_message(c):
            try:
                hf.StoreInput(c.m.sid, "task_id", c.m.kwargs['task_id']).add_value()
                hf.StoreInput(c.m.sid, "activity_type", c.m.kwargs['activity_type']).add_value()
                hf.StoreInput(c.m.sid, "client_id", c.m.client_id).add_value()
                hf.StoreInput(c.m.sid, "language_code", c.m.language_code).add_value()
                sql_statement = f"Select activity_name FROM activity_type WHERE type_id = {c.m.kwargs['activity_type']}"
                activity_name = db.DbQuery(sql_statement, "query_one").create_thread()
                activity_name = ld.activity_name[activity_name][c.m.language_code]
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{notification_evening_title, 
                                 notification_evening_content}'::TEXT[])
                                 WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")

                query_content = db.DbQuery(sql_statement, "query_all").create_thread()
                nickname = db.DbQuery(ss.query("get_nickname", client_id=c.m.client_id), "query_one").create_thread()
                personal_greeting = hf.personal_greetings(nickname, c.m.language_code)
                title = personal_greeting + query_content[0][0].format(activity_name)
                content = query_content[1][0]
                button_left = hf.create_buttons_dict(button_type="cancel", content="no",
                                                     language_code=c.m.language_code,
                                                     wait=True)
                button_right = hf.create_buttons_dict(button_type="ok", content="didit",
                                                      language_code=c.m.language_code,
                                                      wait=True)
                button_middle = hf.create_buttons_dict(button_type="postpone", content="postpone",
                                                       language_code=c.m.language_code)
                buttons = [button_right, button_left, button_middle]
                s.notification_name = "notification/evening"
                s.topic = "eu/agewell/event/reasoner/notification/message"
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('ask_time').when_all(m.button_type == 'ok')
        to('not_done').when_all(m.button_type == 'cancel')
        to('postpone').when_all(m.button_type == 'postpone')

    with stage('ask_time'):
        @run
        def create_message(c):
            try:
                task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
                client_id = hf.StoreInput(c.m.sid, "client_id").get_value()
                language_code = hf.StoreInput(c.m.sid, "language_code", c.m.language_code).get_value()
                sql_statement = f"SELECT duration from task WHERE task_id = {task_id}"
                duration = db.DbQuery(sql_statement, "query_one").create_thread()
                title = ld.activity_done["ask_time_title"][language_code].format(duration)
                content = ld.activity_done["ask_time_content"][language_code]
                button_left = hf.create_buttons_dict(button_type="edit", content="edit",
                                                     language_code=language_code)
                button_right = hf.create_buttons_dict(button_type="ok", content="yes",
                                                      language_code=language_code)
                buttons = [button_right, button_left]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=language_code)
                publish_message(client_id, s.topic, message_dict)
            except Exception as e:
                print (e)

        to('done').when_all(m.button_type == 'ok')
        to('set_time').when_all(m.button_type == 'edit')

    with stage('set_time'):
        @run
        def create_message(c):
            try:
                item_list = [hf.create_items_dict(content_display=ld.minutes[c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(10, 130, 10)])]
                questions = hf.create_question_dict(content_display=[""], items=[item_list])
                questionnaire_type = "time"
                button_right = hf.create_buttons_dict(button_type="ok", content="ok",
                                                      language_code=c.m.language_code)
                buttons = [button_right]
                title = ld.activity_done["set_time_title"][c.m.language_code]
                content = ""
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content,
                                                              buttons=buttons, questions=questions,
                                                              questionnaire_type=questionnaire_type,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print (e)
        to('done').when_all(m.button_type == 'ok')

    with stage('done'):
        @run
        def create_message(c):
            try:
                task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
                try:
                    manual_time = int(c.m.questionnaire_answers[0]["ITEMS"][0]["SELECTED_OPTION_IDS"][0]) * 10
                    sql_statement = f"UPDATE task SET duration={manual_time} WHERE task_id = {task_id}"
                    db.DbQuery(sql_statement, "insert").create_thread()
                except Exception as e:
                    print (e)
                sql_statement = f"UPDATE task SET activity_done='True' WHERE task_id = {task_id}"
                db.DbQuery(sql_statement, "insert").create_thread()
                sql_statement = f"Select content{c.m.language_code} FROM template WHERE daily = 'pos'"
                title = db.DbQuery(sql_statement, "query_one").create_thread()
                sql_statement = (
                    f"Select content{c.m.language_code} FROM template WHERE purpose = 'notification_evening_done'")
                content = db.DbQuery(sql_statement, "query_one").create_thread()
                button_left = hf.create_buttons_dict(button_type="dislike", content="hard",
                                                     language_code=c.m.language_code)
                button_middle = hf.create_buttons_dict(button_type="like", content="right",
                                                       language_code=c.m.language_code)
                button_right = hf.create_buttons_dict(button_type="easy", content="easy",
                                                      language_code=c.m.language_code)
                buttons = [button_right, button_left, button_middle]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('insert_difficulty').when_all(
            (m.button_type == 'easy') | (m.button_type == 'like') | (m.button_type == 'dislike'))

    with stage('not_done'):
        @run
        def create_message(c):
            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{notification_evening_notdone_title, 
                             notification_evening_notdone_content}'::TEXT[])
                             WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
            title = query_content[0][0]
            content = query_content[1][0]
            sql_statement = (f"Select content{c.m.language_code} FROM template WHERE purpose = "
                             f"'reason'")
            reasons = db.DbQuery(sql_statement, "query_all").create_thread()
            item_list = [hf.create_items_dict(
                item_type="single_radio", item_id=1,
                options=[str(i[0]) for i in reasons])
            ]
            questions = hf.create_question_dict(content_display=[""], items=[item_list])
            buttons = [
                hf.create_buttons_dict(button_type="next", content="next", language_code=c.m.language_code, wait=True)]
            message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                          notification_id=c.m.sid,
                                                          title=title, content=content, questions=questions,
                                                          buttons=buttons,
                                                          notification_name=s.notification_name,
                                                          language=c.m.language_code)
            publish_message(c.m.client_id, s.topic, message_dict)


        to('insert_reason').when_all(m.button_type == 'next')

    with stage('postpone'):
        @run
        def get_feedback(c):
            task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
            activity_type = hf.StoreInput(c.m.sid, "activity_type").get_value()
            sql_statement = f"Select activity_name FROM activity_type WHERE type_id = {activity_type}"
            activity_name = db.DbQuery(sql_statement, "query_one").create_thread()
            scheduler_id_evening = c.m.client_id + str(activity_name) + str(datetime.weekday(date.today())) + \
                                   "evening_notification"
            date_for_scheduler = datetime.now() + timedelta(hours=randint(1, 2))
            _schedule.CreateSchedulerJob(date_for_scheduler, c.m.client_id,
                                         scheduler_id=scheduler_id_evening,
                                         activity_type=activity_type, task_id=task_id,
                                         postpone_time="notification/evening",
                                         weekday=datetime.weekday(date.today())).postpone()
            hf.StoreInput(c.m.sid).delete_entry()
            c.delete_state()

    with stage('insert_difficulty'):
        @run
        def create_message(c):
            try:
                task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
                sql_statement = (f"UPDATE task set feedback = '{c.m.button_type}' WHERE "
                                 f" task_id = {task_id}")
                db.DbQuery(sql_statement, "insert").create_thread()
                message_type = {"easy": ["ia", ""],
                                "like": ["pos", ""],
                                "dislike": ["da", ""]}
                purpose = message_type[c.m.button_type]
                sql_queries = ss.query("get_motivational_messages", language_code=c.m.language_code,
                                       purpose=purpose[0], client_id=c.m.client_id)
                content = db.ChooseMessage(sql_queries, c.m.sid, c.m.client_id).choose_right_message()
                button_left = hf.create_buttons_dict(button_type="cancel", content="ignore",
                                                     language_code=c.m.language_code)
                button_right = hf.create_buttons_dict(button_type="ok", content="thanks",
                                                      language_code=c.m.language_code)
                buttons = [button_right, button_left]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              content=content, buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                print(message_dict)
                publish_message(c.m.client_id, s.topic, message_dict)

            except Exception as e:
                print(e)


        to("insert_feedback").when_all(+m.button_type)

    with stage('insert_reason'):
        @run
        def create_message(c):
            try:
                task_id = hf.StoreInput(c.m.sid, "task_id").get_value()
                reasons = {"1": "hard",
                           "2": "time",
                           "3": "motivation",
                           "4": "useful"}
                answer = reasons[str(c.m.questionnaire_answers[0]["ITEMS"][0]["SELECTED_OPTION_IDS"][0])]
                sql_statement = (f"UPDATE task set feedback = '{answer}' WHERE "
                                 f" task_id = {task_id}")
                db.DbQuery(sql_statement, "insert").create_thread()
                message_type = {
                    "hard": ["neu", ""],
                    "time": ["neg", "stg"],
                    "weather": ["neu", ""],
                    "motivation": ["neg", "high"],
                    "useful": ["neg", "low"]}
                purpose = message_type[answer]
                sql_queries = ss.query("get_motivational_messages", language_code=c.m.language_code,
                                       purpose=purpose[0], client_id=c.m.client_id)
                content_first = db.ChooseMessage(sql_queries, c.m.sid, c.m.client_id).choose_right_message()
                print("test")
                if purpose[1] != "":
                    sql_queries = ss.query("get_motivational_messages_alternative", language_code=c.m.language_code,
                                           purpose=purpose[1], client_id=c.m.client_id)
                    content_second = db.ChooseMessage(sql_queries, c.m.sid, c.m.client_id).choose_right_message()
                else:
                    content_second = ""
                content = content_first + content_second
                button_left = hf.create_buttons_dict(button_type="cancel", content="ignore",
                                                     language_code=c.m.language_code)
                button_right = hf.create_buttons_dict(button_type="ok", content="thanks",
                                                      language_code=c.m.language_code)
                buttons = [button_right, button_left]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              content=content, buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                print(message_dict)
                publish_message(c.m.client_id, s.topic, message_dict)

            except Exception as e:
                print(e)


        to("insert_feedback").when_all(+m.button_type)

    with stage('insert_feedback'):
        @run
        def insert_feedback(c):
            try:
                if c.m.button_type == "ok":
                    feedback = 1
                else:
                    feedback = 2
                sql_statement = (f"UPDATE notification SET rating = {feedback} "
                                 f"WHERE notification_id = '{c.m.sid}'")
                db.DbQuery(sql_statement, "insert").create_thread()
            except Exception as e:
                print(e)
            hf.StoreInput(c.m.sid).delete_entry()
            c.delete_state()

with flowchart('ipaq/questionnaire'):
    with stage("input"):
        to('first_question').when_all(+m.client_id)

    with stage('first_question'):
        @run
        def create_message(c):
            try:
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_vigorous, 
                                 ipaq_content_vigorous 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = content[0][0]
                content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                questions = hf.create_question_dict(content_display=[""], items=[item_list])
                buttons = [hf.create_buttons_dict(button_type="next", content="next", wait=True,
                                                  language_code=c.m.language_code)]
                s.questionnaire_type = "ipaq"
                s.topic = "eu/agewell/event/reasoner/notification/message"
                s.notification_name = "ipaq/questionnaire"
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content, questions=questions,
                                                              questionnaire_type=s.questionnaire_type,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('second_question').when_all(m.button_type == 'next')

    with stage('second_question'):
        @run
        def create_message(c):
            try:
                vigorous_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                    range(2)]
                hf.StoreInput(c.m.sid, "vigorous_answers", vigorous_answers).add_value()
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_moderate, 
                                 ipaq_content_moderate 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = content[0][0]
                content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                questions = hf.create_question_dict(content_display=[""], items=[item_list])
                buttons = [hf.create_buttons_dict(button_type="next", content="next", wait=True,
                                                  language_code=c.m.language_code)]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content, questions=questions,
                                                              questionnaire_type=s.questionnaire_type,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('third_question').when_all(m.button_type == 'next')

    with stage('third_question'):
        @run
        def create_message(c):
            try:
                moderate_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                    range(2)]
                hf.StoreInput(c.m.sid, "moderate_answers", moderate_answers).add_value()
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_walking, 
                                 ipaq_content_walking 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = content[0][0]
                content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                questions = hf.create_question_dict(content_display=[""], items=[item_list])
                buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                                  language_code=c.m.language_code, wait=True)]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content, questions=questions,
                                                              questionnaire_type=s.questionnaire_type,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)

            except Exception as e:
                print(e)


        to('save_answers').when_all(m.button_type == 'ok')

    with stage('save_answers'):
        @run
        def save_answers(c):
            try:
                walking_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                   range(2)]
                vigorous_answers = hf.StoreInput(c.m.sid, "vigorous_answers").get_value()
                moderate_answers = hf.StoreInput(c.m.sid, "moderate_answers").get_value()

                ipaq_value = (vigorous_answers[0] - 1) * (vigorous_answers[1] * 10) * 8 + (moderate_answers[0] - 1) * (
                        moderate_answers[1] * 10) * \
                             4 + (walking_answers[0] - 1) * (walking_answers[1] * 10) * 3.3
                ipaq_value = int(round(ipaq_value, -2))
                sql_statement = (f"UPDATE user_info SET value_ipaq = {ipaq_value} WHERE "
                                 f"user_id='{c.m.client_id}'")
                db.DbQuery(sql_statement, "insert").create_thread()
                if ipaq_value < 300:
                    ipaq_value = 300
                sql_statement = f"UPDATE goal SET met_required={ipaq_value} WHERE user_id='{c.m.client_id}'"
                db.DbQuery(sql_statement, "insert").create_thread()

                sql_statement = f"Select content{c.m.language_code} FROM template WHERE purpose='ipaq_credits'"
                content = db.DbQuery(sql_statement, "query_one").create_thread()
                content = content.format(ipaq_value)
                buttons = [hf.create_buttons_dict(button_type="ok", content="ok",
                                                  language_code=c.m.language_code, wait=True)]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              content=content,
                                                              questionnaire_type=s.questionnaire_type,
                                                              buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, s.topic, message_dict)
                sql_statement = f"SELECT value_mpam from user_info WHERE user_id='{c.m.client_id}'"
                mpam_done = db.DbQuery(sql_statement, "query_one").create_thread()
                if mpam_done is None:
                    mpam = 0
                else:
                    mpam = 1
                c.assert_fact({'mpam': mpam})
            except Exception as e:
                print(e)


        to('go_to_mpam').when_all(m.button_type == 'ok', m.mpam == 0)
        to('delete_ipaq_state').when_all(m.button_type == 'ok', m.mpam == 1)

    with stage('delete_ipaq_state'):
        @run
        def delete(c):
            c.delete_state()

    with stage('go_to_mpam'):
        @run
        def show_credits(c):
            hf.StoreInput(c.m.sid).delete_entry()
            post("mpam/questionnaire", {"sid": c.m.sid, "client_id": c.m.client_id, "language_code": c.m.language_code})

with flowchart('mpam/questionnaire'):
    with stage("input"):
        to('question').when_all(+m.client_id)

    with stage('question'):
        @run
        def create_message(c):
            try:
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 mpam_title, 
                                 mpam_content 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                title = content[0][0]
                content = content[1][0]
                options = [ld.mpam["false"][c.m.language_code], "", "", "", ld.mpam["true"][c.m.language_code]]
                content_display = [ld.mpam["enjoyment"][c.m.language_code],
                                   ld.mpam["appearance"][c.m.language_code],
                                   ld.mpam["social"][c.m.language_code],
                                   ld.mpam["fitness"][c.m.language_code],
                                   ld.mpam["competence"][c.m.language_code]]
                item_list = [hf.create_items_dict(content_display=j,
                                                  item_type="single_likert_5", item_id=i + 1,
                                                  options=options) for i, j in enumerate(content_display)
                             ]

                questions = hf.create_question_dict(content_display=[""],
                                                    items=[item_list])
                buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                                  language_code=c.m.language_code)]
                questionnaire_type = "mpam"
                topic = "eu/agewell/event/reasoner/notification/message"
                notification_name = "mpam/questionnaire"
                message_dict = jd.create_notification_message(topic=topic, client_id=c.m.client_id,
                                                              notification_id=c.m.sid,
                                                              title=title, content=content, questions=questions,
                                                              questionnaire_type=questionnaire_type,
                                                              buttons=buttons,
                                                              notification_name=notification_name,
                                                              language=c.m.language_code)
                publish_message(c.m.client_id, topic, message_dict)
            except Exception as e:
                print(e)


        to('save_answers').when_all(m.button_type == 'ok')

    with stage('save_answers'):
        @run
        def save_answers(c):
            try:
                values = str([c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                              range(len(c.m.questionnaire_answers[0]["ITEMS"]))])
                values = values.replace('[', '{').replace(']', '}').replace('\'', '\"')
                sql_statement = (f"UPDATE user_info SET value_mpam = '{values}' WHERE "
                                 f"user_id='{c.m.client_id}'")
                db.DbQuery(sql_statement, "insert").create_thread()
                c.delete_state()
            except Exception as e:
                print(e)


with ruleset('activity/missed'):
    @when_all(+m.client_id)
    def send_activites_missed(c):
        topic = "eu/agewell/event/reasoner/notification/message"
        notification_name = "user/activity/missed"
        notification_id = "999"
        buttons = [hf.create_buttons_dict(button_type="ok", content="ok",
                                          language_code=c.m.language_code)]
        title = ld.title_goal_screen["activity_missed"][c.m.language_code]
        content = ld.text_to_speech["activity_missed"][c.m.language_code].format(c.m.nickname)
        message_dict = jd.create_notification_message(topic=topic, client_id=c.m.client_id,
                                                      notification_id="999",
                                                      title=title, content=content,
                                                      buttons=buttons,
                                                      notification_name=notification_name,
                                                      language=c.m.language_code)
        publish_message(c.m.client_id, topic, message_dict)

with ruleset('dashboard'):
    try:
        @when_all(+m.input)
        def check_number_week(c):

            c.post({'len_weeks': len(c.m.input), 'weeks': c.m.input, "language": c.m.language})


        @when_all(m.len_weeks == 1)
        def first_week(c):

            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["first_week"][c.m.language]).append_value()
            c.post({"percentage_current_week": c.m.weeks, "language": c.m.language})


        @when_all(m.len_weeks == 2)
        def second_week(c):
            goal_list = [i[1] for i in c.m.weeks]
            difference_lt = hf.difference_last_two(goal_list)
            c.post({"percentage_current_week": c.m.weeks, "language": c.m.language})
            c.post({"difference_lt": difference_lt, "language": c.m.language, "second_week": "yes"})


        @when_all(m.len_weeks > 2)
        def more_than_two_weeks(c):
            last_five = c.m.weeks[-5:]
            achieved_list = [i[0] for i in last_five]
            goal_list = [i[1] for i in last_five]
            difference_fl = hf.difference_first_last(goal_list)
            difference_lt = hf.difference_last_two(goal_list)
            mov_avg = np.diff(hf.moving_average(np.array(goal_list), n=len(goal_list) - 1))[0]
            times_achieved_goal = hf.achieved_goal(last_five)
            times_exceeded_goal = hf.exceeding_goal(last_five)
            variability = hf.get_variability(achieved_list)
            streak = hf.get_streak(last_five)
            c.post({"difference_fl": difference_fl, "no_weeks": len(last_five) - 1, "language": c.m.language})
            c.post({"mov_avg": mov_avg, "language": c.m.language})
            c.post(
                {"times_achieved_goal": times_achieved_goal, "no_weeks": len(last_five) - 1, "language": c.m.language})
            c.post({"times_exceeded_goal": times_exceeded_goal, "language": c.m.language})
            c.post({"difference_lt": difference_lt, "language": c.m.language})
            c.post({"streak": streak, "language": c.m.language})
            c.post({"variability": variability, "language": c.m.language})
            c.post({"percentage_current_week": last_five, "language": c.m.language})


        @when_all(+m.percentage_current_week)
        def percentage_done_current_week(c):
            percentage_done = int(c.m.percentage_current_week[-1][0] * 100 / c.m.percentage_current_week[-1][1])
            hf.StoreInput(c.m.sid, "dashboard",
                       ld.dashboard_desc["current_week"][c.m.language].format(percentage_done)).append_value()


        @when_all(m.difference_fl > 0)
        def goal_difference_pos(c):
            hf.StoreInput(c.m.sid, "dashboard",
                       ld.dashboard_desc["fl_pos"][c.m.language].format(c.m.difference_fl, c.m.no_weeks)).append_value()


        @when_all(m.difference_fl < 0)
        def goal_difference_neg(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["fl_neg"][c.m.language].format(c.m.no_weeks, abs(
                c.m.difference_fl))).append_value()


        @when_all(m.difference_fl == 0)
        def goal_stayed_same(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["fl_neu"][c.m.language].format(c.m.no_weeks)).append_value()


        @when_all(m.difference_lt == 0)
        def goal_stayed_same(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["lt_neu"][c.m.language]).append_value()


        @when_all(m.difference_lt > 0)
        def goal_difference_pos(c):
            hf.StoreInput(c.m.sid, "dashboard",
                       ld.dashboard_desc["lt_pos"][c.m.language].format(c.m.difference_lt)).append_value()


        @when_all(m.difference_lt < 0)
        def goal_difference_neg(c):
            if c.m.second_week == "yes":
                hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["lt_neg_second"][c.m.language]).append_value()
            else:
                hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["lt_neg"][c.m.language]).append_value()


        @when_all(m.mov_avg > 0)
        def mov_avg_pos(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["mov_avg_pos"][c.m.language]).append_value()


        @when_all(m.mov_avg < 0)
        def mov_avg_neg(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["mov_avg_neg"][c.m.language]).append_value()


        @when_all(c.first << m.times_achieved_goal > 0,
                  c.second << m.times_exceeded_goal == 0)
        def check_how_many_times(c):
            if c.first.times_achieved_goal == 1:
                times_achieved_goal = ld.dashboard_desc["once"]["c.m.language"]
            else:
                times_achieved_goal = str(c.first.times_achieved_goal) + ld.dashboard_desc["multiple"][
                    c.first.language]
            if c.first.no_weeks / c.first.times_achieved_goal <= 2:
                hf.StoreInput(c.m.sid, "dashboard",
                           ld.dashboard_desc["times_achieved_goal_singular_pos"][c.first.language].format(
                               times_achieved_goal, c.first.no_weeks)).append_value()
            else:
                hf.StoreInput(c.m.sid, "dashboard",
                           ld.dashboard_desc["times_achieved_goal_singular_neg"][c.first.language].format(
                               times_achieved_goal,
                               c.first.no_weeks)).append_value()


        @when_all(c.first << m.times_achieved_goal > 0,
                  c.second << m.times_exceeded_goal > 0)
        def exceeded(c):
            if c.first.times_achieved_goal == 1:
                times_achieved_goal = ld.dashboard_desc["once"][c.first.language]
            else:
                times_achieved_goal = str(c.first.times_achieved_goal) + ld.dashboard_desc["multiple"][
                    c.first.language]
            if c.second.times_exceeded_goal == 1:
                times_exceeded_goal = ld.dashboard_desc["once"][c.first.language]
            else:
                times_exceeded_goal = str(c.second.times_exceeded_goal) + ld.dashboard_desc["multiple"][
                    c.first.language]
            hf.StoreInput(c.first.sid, "dashboard",
                       ld.dashboard_desc["times_exceeded_goal"][c.first.language].format(times_achieved_goal,
                                                                                      c.first.no_weeks,
                                                                                      times_exceeded_goal)).append_value()


        @when_all(m.streak > 1)
        def streak(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["streak"][c.m.language].format(c.m.streak)).append_value()


        @when_all(m.streak <= 1)
        def streak(c):
            pass


        @when_all(m.variability >= 1)
        def high_variability(c):
            hf.StoreInput(c.m.sid, "dashboard", ld.dashboard_desc["variability"][c.m.language]).append_value()


        @when_all(m.variability < 1)
        def low_variability(c):
            pass


        @when_all(m.action == "delete")
        def delete_user_state(c):
            c.delete_state()

    except Exception as e:
        print(e)