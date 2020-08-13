import _jsondicts as jd
import _helperfunctions as hf
import _databasefunctions as db
from durable.lang import *
from datetime import datetime, timedelta, date
import uuid
import _schedule
from _mqttconnection import publish_message
import _languagedicts as ld


def execute_scheduler_job(scheduler_event, client_id, scheduler_id=None, **kwargs):
    notification_id = uuid.uuid1().int
    sql_statement = f"SELECT language from user_info WHERE user_id = '{client_id}'"
    language_code = db.DbQuery(sql_statement, "query_one").create_thread()

    post(scheduler_event,
         {"sid": notification_id, "client_id": client_id, "scheduler_id": scheduler_id,
          "language_code": language_code, "kwargs": kwargs})


with ruleset('notification/response'):
    @when_all(+m.client_id)
    def post_to_ruleset(c):
        print("Response is here")
        post(c.m.notification_name,
             {"sid": int(c.m.notification_id), "button_type": c.m.button_type,
              "questionnaire_answers": c.m.questionnaire_answers["ANSWERS"], "client_id": c.m.client_id,
              "language_code": c.m.language_code})


# ruleset which is triggered internally from preference/message when client_id is not yet present.
# triggers scheduler job for ruleset firstgoal/intern
with ruleset('clientid/message'):
    @when_all(+m.client_id)
    def create_user(c):
        try:
            sql_statement = f"INSERT INTO user_info(user_id) VALUES ('{c.m.client_id}') ON CONFLICT DO NOTHING"
            db.DbQuery(sql_statement, "insert").create_thread()
            sql_statement = (
                f"UPDATE user_info SET language = '{c.m.language_code}' WHERE user_id = "
                f"'{c.m.client_id}'")
            db.DbQuery(sql_statement, "insert").create_thread()

            """for testing:
            run_time = datetime.now() + timedelta(seconds=2)
            _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", run_date=run_time,
                                        args=["firstgoal/intern", c.m.client_id])"""

            post("firstgoal/intern", {"client_id": c.m.client_id, "language_code": c.m.language_code})
        except Exception as e:
            print(e)

with ruleset('firstgoal/intern'):
    @when_all(+m.client_id)
    def create_goal_notification(c):
        try:
            notification_id = str(uuid.uuid1().int)
            run_time = datetime.now() + timedelta(days=7)
            run_time = run_time.replace(hour=23, minute=59)
            sql_statement_goal = (f"INSERT INTO goal(user_id, start_date, end_date, met_required) VALUES "
                                  f"('{c.m.client_id}','{date.today()}','{run_time}', {1000})")
            db.DbQuery(sql_statement_goal, "insert").create_thread()
            _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", run_date=run_time,
                                        args=["goal", c.m.client_id])

            """for testing:
            run_time_questionnaires = datetime.now() + timedelta(seconds=5)
            _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", run_date=run_time_questionnaires,
                                        args=["ipaq/questionnaire", c.m.client_id])
            _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", run_date=run_time_questionnaires,
                                        args=["mpam/questionnaire", c.m.client_id])"""

            sql_statement = f"SELECT language FROM user_info WHERE user_id = '{c.m.client_id}'"
            language_code = db.DbQuery(sql_statement, "query_one").create_thread()
            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{first_goal_title, 
                             first_goal_text}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
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
            sql_statement = f"SELECT user_id from user_info WHERE user_id = '{c.m.client_id}'"
            existing = db.DbQuery(sql_statement, "query_one").create_thread()
            if existing:
                sql_statement = (
                    f"UPDATE user_info SET language = '{c.m.language_code}' WHERE user_id = "
                    f"'{c.m.client_id}'")
                db.DbQuery(sql_statement, "insert").create_thread()
                try:
                    sql_statement = (f"UPDATE user_info SET age = {c.m.preferences['userYearOfBirth']}, "
                                     f"nickname = '{c.m.preferences['userName']}', "
                                     f"morning_reminder_id = '{c.m.preferences['reminderTimeIndex']}', "
                                     f"evening_reminder_id = '{c.m.preferences['questionnaireTimeIndex']}' "
                                     f"WHERE user_id = '{c.m.client_id}'")
                    db.DbQuery(sql_statement, "insert").create_thread()
                except:
                    pass
            else:
                post("clientid/message", {"client_id": c.m.client_id, "language_code": c.m.language_code})

        except Exception as e:
            print(e)

with ruleset('user/activity/edit/request'):
    @when_all(m.dimension_id == 1)
    def get_activity_types(c):
        try:
            try:
                sql_statement = (f"SELECT max(m.type_id), max(m.duration) as duration, ARRAY_AGG(s.start_daytime) "
                                 f"as selected_days, max(s.duration) as selected_duration from activity_type m, task s "
                                 f"WHERE s.active='True' and m.type_id = {int(c.m.activity_id)} and s.activity_id = "
                                 f"(SELECT MAX(a.activity_id) from activity a WHERE a.user_id = "
                                 f"'{c.m.client_id}' and a.goal_id = (SELECT c.goal_id from goal c "
                                 f"WHERE CURRENT_TIMESTAMP between c.start_date and c.end_date and "
                                 f"c.user_id = '{c.m.client_id}')) GROUP BY m.activity_name")

                activity_types = db.DbQuery(sql_statement, "query_all").create_thread()
                print(activity_types)
                type_id = activity_types[0][0]
                duration = activity_types[0][1]
                duration = hf.convert_to_string(duration)
                selected_days = [i.weekday() for i in activity_types[0][2]]
                # selected_days = hf.convert_to_string(selected_days)
                selected_duration = str(activity_types[0][3])
            except:
                sql_statement = (f"SELECT max(m.type_id), max(m.duration) as duration, ARRAY_AGG(s.start_daytime) "
                                 f"as selected_days, max(s.duration) as selected_duration from activity_type m, task s "
                                 f"WHERE m.type_id = {int(c.m.activity_id)} and s.activity_id = "
                                 f"(SELECT MAX(a.activity_id) from activity a WHERE a.user_id = "
                                 f"'{c.m.client_id}' and a.goal_id = (SELECT c.goal_id from goal c "
                                 f"WHERE CURRENT_TIMESTAMP between c.start_date and c.end_date and "
                                 f"c.user_id = '{c.m.client_id}')) GROUP BY m.activity_name")

                activity_types = db.DbQuery(sql_statement, "query_all").create_thread()
                print(activity_types)
                type_id = activity_types[0][0]
                duration = activity_types[0][1]
                duration = hf.convert_to_string(duration)
                selected_days = []
                # selected_days = hf.convert_to_string(selected_days)
                selected_duration = ""
            sql_statement = (f"SELECT s.end_date from goal s where user_id = '{c.m.client_id}' and s.end_date > "
                             f"CURRENT_TIMESTAMP")
            end_date = db.DbQuery(sql_statement, "query_one").create_thread()
            start_date = datetime.now()
            days_activity = []
            if end_date is not None:
                for dt in hf.daterange(start_date, end_date):
                    days_activity.append({"ID": datetime.weekday(dt),
                                          "CONTENT_DISPLAY": ld.weekDays[c.m.language_code][datetime.weekday(dt)]})
            days_activity = [i for n, i in enumerate(days_activity) if i not in days_activity[n + 1:]]
            topic = "eu/agewell/event/reasoner/user/activity/edit/response"
            message_dict = jd.create_activity_types_edit_message(topic=topic, client_id=c.m.client_id,
                                                                 days=days_activity, selected_days=selected_days,
                                                                 selected_duration=selected_duration,
                                                                 activity_id=type_id,
                                                                 language=c.m.language_code, duration=duration)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)
# ruleset which returns actìvities which are currently not chosen by the user. Includes time, day and info
with ruleset('activitytypes/request'):
    @when_all(m.dimension_id == 1)
    def get_activity_types(c):
        try:
            sql_statement = (f"SELECT max(m.type_id) as type_id, m.activity_name, max(m.duration) as duration, "
                             f"ARRAY_AGG(s.content{c.m.language_code}) as content, ARRAY_AGG (category) "
                             f"as category, max(m.url) from activity_type m, template s WHERE m.activity_name = s.activity "
                             f"and m.type_id NOT IN (SELECT b.type_id from activity b WHERE b.user_id = "
                             f"'{c.m.client_id}' and b.activity_id in (SELECT s.activity_id FROM task s WHERE "
                             f"s.active = 'True') and b.goal_id = (SELECT b.goal_id from goal b "
                             f"WHERE CURRENT_TIMESTAMP between b.start_date and b.end_date and "
                             f"b.user_id = '{c.m.client_id}')) GROUP BY activity_name")

            activity_types = db.DbQuery(sql_statement, "query_all").create_thread()
            sql_statement = (f"SELECT s.end_date from goal s where user_id = '{c.m.client_id}' and s.end_date > "
                             f"CURRENT_TIMESTAMP")
            start_date = datetime.now()
            end_date = db.DbQuery(sql_statement, "query_one").create_thread()
            days_activity = []
            if end_date is not None:
                for dt in hf.daterange(start_date, end_date):
                    days_activity.append({"ID": datetime.weekday(dt),
                                          "CONTENT_DISPLAY": ld.weekDays[c.m.language_code][datetime.weekday(dt)]})
            days_activity = [i for n, i in enumerate(days_activity) if i not in days_activity[n + 1:]]
            topic = "eu/agewell/event/reasoner/activitytypes/response"
            message_dict = jd.create_activity_types_message(topic=topic, client_id=c.m.client_id,
                                                            types=activity_types, days=days_activity,
                                                            language=c.m.language_code)
            publish_message(c.m.client_id, topic, message_dict)
        except Exception as e:
            print(e)

# ruleset which creates a message to show the met value of the current choice as well as left weekly mets after the
# choice
with ruleset('creditsinformation/request'):
    @when_all(m.dimension_id == 1)
    def insert_user_preferences(c):
        try:
            sql_statement = f"SELECT met_value from activity_type WHERE type_id = {c.m.activity_id}"
            met_value = db.DbQuery(sql_statement, "query_one").create_thread()
            try:
                met_calculation = met_value * int(c.m.selected_duration) * len(c.m.selected_days)
            except Exception as e:
                print(e)
                met_calculation = 0
            sql_statement = (
                f"SELECT content{c.m.language_code} FROM template WHERE purpose = 'credits_information_general'")
            message_constellation_general = db.DbQuery(sql_statement, "query_one").create_thread()
            message_constellation_general = message_constellation_general.format(met_calculation)

            sql_statement = (f"SELECT met_required from goal where CURRENT_TIMESTAMP between start_date and end_date "
                             f"and user_id = '{c.m.client_id}'")
            weekly_goal_mets = db.DbQuery(sql_statement, "query_one").create_thread()
            if weekly_goal_mets is None:
                weekly_goal_mets = 0
            sql_statement = (f"SELECT b.duration, s.met_value from task b "
                             f"INNER JOIN activity m ON b.activity_id = m.activity_id "
                             f"INNER JOIN activity_type s ON s.type_id = m.type_id "
                             f"WHERE b.active = True and m.activity_id IN "
                             f" (SELECT m.activity_id from activity m WHERE m.goal_id = "
                             f"(SELECT b.goal_id from goal b where CURRENT_TIMESTAMP between b.start_date and "
                             f"b.end_date "
                             f"and user_id = '{c.m.client_id}') and m.type_id!={c.m.activity_id})")

            active_mets = db.DbQuery(sql_statement, "query_all").create_thread()
            print(active_mets)
            active_mets = sum(i[0] * i[1] for i in active_mets)
            print(active_mets)
            left_mets = weekly_goal_mets - (met_calculation + active_mets)
            print(left_mets)
            if left_mets > 50:
                scnd_msg = "credits_information_more"
                mets_msg = left_mets
            elif left_mets < -50:
                scnd_msg = "credits_information_less"
                mets_msg = abs(left_mets)
            else:
                scnd_msg = "credits_information_stay"

            sql_statement = f"SELECT content{c.m.language_code} FROM template WHERE purpose = '{scnd_msg}'"
            message_constellation_specific = db.DbQuery(sql_statement, "query_one").create_thread()
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
with ruleset('user/activities/message'):
    @when_all(+m.client_id)
    def insert_user_activity(c):
        try:
            sql_statement = (f"INSERT INTO activity(user_id, goal_id, type_id) SELECT "
                             f"'{c.m.client_id}', (SELECT s.goal_id from goal s where CURRENT_TIMESTAMP between "
                             f"s.start_date and s.end_date "
                             f"and user_id = '{c.m.client_id}'), {c.m.activity_id} ON CONFLICT DO NOTHING")
            print(sql_statement)
            db.DbQuery(sql_statement, "insert").create_thread()

            dates_for_tasks = []
            sql_statement = f"Select morning_reminder_id from user_info WHERE user_id='{c.m.client_id}'"
            reminder_id_morning = db.DbQuery(sql_statement, "query_one").create_thread()
            if reminder_id_morning is None:
                reminder_id_morning = "not_defined"
            sql_statement = f"Select evening_reminder_id from user_info WHERE user_id='{c.m.client_id}'"
            reminder_id_evening = db.DbQuery(sql_statement, "query_one").create_thread()
            if reminder_id_evening is None:
                reminder_id_evening = "not_defined"
            try:
                test_if_emty = c.m.selected_days[0]
                for day in c.m.selected_days:
                    day = int(day)
                    date_for_scheduler = hf.next_weekday(day)
                    date_for_task = datetime.strftime(hf.next_weekday(day), "%d/%m/%Y")
                    dates_for_tasks.append(date_for_task)
                    sql_statement = (f"INSERT INTO task(activity_id, duration, start_daytime, active) SELECT "
                                     f"(SELECT activity_id from activity where user_id = '{c.m.client_id}' and "
                                     f"goal_id = ( "
                                     f"SELECT s.goal_id from goal s where "
                                     f"CURRENT_TIMESTAMP between s.start_date and s.end_date and user_id = " 
                                     f"'{c.m.client_id}') and type_id = {c.m.activity_id}), "
                                     f"{int(c.m.selected_duration)}, '{date_for_task}', True  ON CONFLICT ON CONSTRAINT "
                                     f"task_activity_id_start_daytime_key DO UPDATE SET active='True', duration= "
                                     f"{int(c.m.selected_duration)} RETURNING task_id")
                    print(sql_statement)
                    task_id = db.DbQuery(sql_statement, "insert").create_thread()
                    scheduler_id_morning = c.m.client_id + str(c.m.activity_id) + str(day) + "morning_notification"
                    scheduler_id_evening = c.m.client_id + str(c.m.activity_id) + str(day) + "evening_notification"
                    _schedule.CreateSchedulerJob(date_for_scheduler, c.m.client_id, reminder_id_morning,
                                                 scheduler_id=scheduler_id_morning,
                                                 activity_type=c.m.activity_id,
                                                 duration=int(c.m.selected_duration)).morning_notification()
                    _schedule.CreateSchedulerJob(date_for_scheduler, c.m.client_id, reminder_id_evening,
                                                 scheduler_id=scheduler_id_evening,
                                                 activity_type=c.m.activity_id, task_id=task_id).evening_notification()
            except IndexError:
                pass
            if len(dates_for_tasks) > 1:
                sql_statement = (
                    f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from activity where "
                    f"user_id = '{c.m.client_id}' "
                    f"and type_id = {c.m.activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                    f"CURRENT_TIMESTAMP "
                    f"between s.start_date and s.end_date "
                    f"and user_id = '{c.m.client_id}')) and start_daytime NOT IN {tuple(dates_for_tasks)}")
            elif len(dates_for_tasks) == 1:
                dates_for_tasks = dates_for_tasks[0]
                sql_statement = (
                    f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from activity where "
                    f"user_id = '{c.m.client_id}' "
                    f"and type_id = {c.m.activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                    f"CURRENT_TIMESTAMP "
                    f"between s.start_date and s.end_date "
                    f"and user_id = '{c.m.client_id}')) and start_daytime NOT IN ('{dates_for_tasks}')")
            else:
                sql_statement = (
                    f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from activity where "
                    f"user_id = '{c.m.client_id}' "
                    f"and type_id = {c.m.activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                    f"CURRENT_TIMESTAMP "
                    f"between s.start_date and s.end_date "
                    f"and user_id = '{c.m.client_id}'))")
            print(sql_statement)
            db.DbQuery(sql_statement, "insert").create_thread()
        except Exception as e:
            print(e)

# provides a short overview of the weekly progress with text and percentage done
with ruleset('dimension/request'):
    @when_all(+m.client_id)
    def get_dimension_info(c):
        try:
            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{dashboard_title, 
                             dashboard_content}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            content = db.DbQuery(sql_statement, "query_all").create_thread()
            sql_statement = (f"SELECT met_required from goal where CURRENT_TIMESTAMP between start_date and end_date "
                             f"and user_id = '{c.m.client_id}'")
            weekly_goal_mets = db.DbQuery(sql_statement, "query_one").create_thread()
            if weekly_goal_mets is None:
                weekly_goal_mets = 0
            sql_statement = (f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                             f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                             f"activity.activity_id WHERE a.active='True' and a.activity_done='True'"
                             f"and a.activity_id IN (SELECT m.activity_id from activity m WHERE m.goal_id = "
                             f"(SELECT b.goal_id from goal b where CURRENT_TIMESTAMP "
                             f"between b.start_date and b.end_date  and user_id = '{c.m.client_id}'))")

            done_mets = db.DbQuery(sql_statement, "query_all").create_thread()
            print(done_mets)
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

            sql_statement = f"Select content{c.m.language_code} FROM template WHERE purpose = '{scnd_msg}'"
            dashboard_motivation = db.DbQuery(sql_statement, "query_one").create_thread()

            topic = "eu/agewell/event/reasoner/dimension/response"
            title = content[0][0]
            # todo: should be queried in different languages
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
            # get goal mets and goal info
            sql_statement = (f"SELECT met_required from goal where CURRENT_TIMESTAMP between start_date and end_date "
                             f"and user_id = '{c.m.client_id}'")
            weekly_goal_mets = db.DbQuery(sql_statement, "query_one").create_thread()
            if weekly_goal_mets == None:
                weekly_goal_mets = 0
            sql_statement = (f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                             f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                             f"activity.activity_id WHERE a.active='True' and a.activity_id IN (SELECT m.activity_id "
                             f"from "
                             f"activity m WHERE m.goal_id = (SELECT b.goal_id from goal b where CURRENT_TIMESTAMP "
                             f"between b.start_date and b.end_date  and user_id = '{c.m.client_id}'))")
            allocated_mets = db.DbQuery(sql_statement, "query_all").create_thread()
            print(allocated_mets)
            try:
                allocated_mets = sum(i[0] * i[1] for i in allocated_mets)
                if allocated_mets > weekly_goal_mets:
                    allocated_mets = weekly_goal_mets
                left_mets = weekly_goal_mets - allocated_mets
            except:
                allocated_mets = 0
                left_mets = weekly_goal_mets

            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{goalinfo_info, 
                             goalinfo_achieved, goalinfo_remaining,
                              goalinfo_activities}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
            goalinfo_info = query_content[0][0].format(weekly_goal_mets)
            goalinfo_achieved = query_content[1][0].format(allocated_mets)

            if left_mets != 0:
                goalinfo_remaining = query_content[2][0].format(left_mets)
            else:
                goalinfo_remaining = ""

            goalinfo_activities = query_content[3][0]
            goalinfo_1 = goalinfo_info + goalinfo_achieved + goalinfo_remaining + goalinfo_activities

            sql_statement = (f"SELECT s.activity_name, ARRAY_AGG(a.start_daytime), max(a.duration) as duration,"
                             f"count(CASE WHEN a.activity_done THEN 1 END), max(s.met_value) as met_value, "
                             f"max(s.type_id), max(s.url) from "
                             f"activity_type s INNER JOIN activity m ON s.type_id = m.type_id "
                             f"INNER JOIN task a ON a.activity_id = m.activity_id WHERE a.active = 'True' and "
                             f"m.activity_id IN (SELECT a.activity_id WHERE a.active = 'True') and "
                             f"m.goal_id = ( "
                             f"SELECT m.goal_id from goal m where CURRENT_TIMESTAMP between m.start_date "
                             f"and m.end_date and m.user_id = '{c.m.client_id}') GROUP BY s.activity_name")

            activity_infos = db.DbQuery(sql_statement, "query_all").create_thread()

            activity_infos = [
                {"activity_name": ld.activity_name[i[0]][c.m.language_code],
                 "days": [ld.weekDays[c.m.language_code][j.weekday()] for j in i[1]], "activity_duration": i[2],
                 "activities_done": i[3], "met_value": i[4], "type_id": i[5], "url": i[6],
                 "activity_name_english": i[0]}
                for i in activity_infos
            ]

            goal_text = goalinfo_1
            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{goalinfo_activity_days, 
                             goalinfo_activity_info, 
                             goalinfo_activity_achieved, 
                             goalinfo_activity_completed}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")

            goalinfo_text = db.DbQuery(sql_statement, "query_all").create_thread()

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
                goalinfo_days = goalinfo_text[0][0].format(i["activity_name"].capitalize(),
                                                           ' and '.join(i["days"]),
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

                dict_for_activity = {"ID": i["type_id"], "TITLE_DISPLAY": i["activity_name"],
                                     "CREDIT_SCORE": i["activity_duration"] * i["met_value"] * len(i["days"]),
                                     "CREDIT_DONE": i["activity_duration"] * i["met_value"] * i["activities_done"],
                                     "CONTENT_DISPLAY": (
                                         " ".join(': '.join(w) for w in
                                                  zip(activity_content[h][2], activity_content[h][1]))),
                                     "CONTENT_IMAGE": i["url"]}
                # todo push it to function to choose bullet point automatically
                activity_list.append(dict_for_activity)
            topic = "eu/agewell/event/reasoner/user/activities/response"
            message_dict = jd.create_useractivity_notification(topic=topic, client_id=c.m.client_id,
                                                               goal_credits=weekly_goal_mets,
                                                               goal_content_display=goal_text,
                                                               activities_list=activity_list,
                                                               language=c.m.language_code)

            publish_message(c.m.client_id, topic, message_dict)
        except Exception  as e:
            print(e)

with flowchart("goal"):
    # calculate percentage of goal done and adjust the new goal dependent
    # on the credits of the old goal
    with stage("input"):
        to('info').when_all(+m.client_id)

    with stage('info'):
        @run
        def create_goal_notification(c):
            try:
                s.client_id = c.m.client_id
                run_time = datetime.now() + timedelta(days=7)
                run_time = run_time.replace(hour=23, minute=59)
                _schedule.scheduler.add_job(execute_scheduler_job, trigger="date", run_date=run_time,
                                            args=["goal", c.m.client_id])
                sql_statement = (f"SELECT goal_id, met_required from goal where user_id = '{c.m.client_id}' "
                                 f"ORDER BY goal_id DESC LIMIT 1")
                goal_vars = db.DbQuery(sql_statement, "query_all").create_thread()
                goal_id = goal_vars[0][0]
                goal_mets = goal_vars[0][1]

                sql_statement = (f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                                 f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                                 f"activity.activity_id WHERE a.active='True' and a.activity_done='True'"
                                 f"and a.activity_id IN (SELECT m.activity_id from activity m WHERE " 
                                 f"m.goal_id = {goal_id})")
                done_mets = db.DbQuery(sql_statement, "query_all").create_thread()
                try:
                    done_mets = sum(i[0] * i[1] for i in done_mets)
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
                print(query_content)
                title = query_content[0][0]
                content_1 = query_content[1][0].format(percentage_done_mets)

                if percentage_done_mets == 75:
                    new_goal = goal_mets
                    content_2 = query_content[2][0]
                else:
                    if percentage_done_mets > 75:
                        increase_decrease_mets = int((percentage_done_mets - 75) * 100 / goal_mets)
                        new_goal = goal_mets + increase_decrease_mets
                        increase_decrease = query_content[4][0]
                    if percentage_done_mets < 75:
                        increase_decrease_mets = int(goal_mets / 100 * (-0.3333 * percentage_done_mets + 25))
                        new_goal = goal_mets - increase_decrease_mets
                        increase_decrease = query_content[5][0]

                    content_2 = query_content[3][0].format(increase_decrease, increase_decrease_mets, new_goal)
                    print(content_2)

                sql_statement = (f"INSERT INTO goal(user_id, start_date, end_date, met_required) VALUES "
                                      f"('{c.m.client_id}','{date.today()}','{run_time}', {new_goal})")
                db.DbQuery(sql_statement, "insert").create_thread()
                s.new_goal_mets = new_goal
                content = content_1 + content_2
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
                print(message_dict)

                publish_message(s.client_id, s.topic, message_dict)
            except Exception as e:
                print(e)


        to('adjustment').when_all(m.button_type == "edit")

    with stage('adjustment'):
        @run
        def create_adjustment_goal_notification(c):
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
            s.increase_decrease_values = {"1": 100, "2": 300, "3": s.new_goal_mets, "4": 100, "5": 300}
            increase_decrease_text = [increase_question.format(s.increase_decrease_values["1"]),
                                      increase_question.format(s.increase_decrease_values["2"]),
                                      maintain_question.format(s.increase_decrease_values["3"]),
                                      decrease_question.format(s.increase_decrease_values["4"]),
                                      decrease_question.format(s.increase_decrease_values["5"])]
            item_list = [hf.create_items_dict(
                item_type="single_radio", item_id=1,
                options=[str(i) for i in increase_decrease_text])
            ]
            questions = hf.create_question_dict(content_display=[""], items=[item_list])
            buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                              language_code=c.m.language_code)]
            message_dict = jd.create_notification_message(topic=s.topic, client_id=s.client_id,
                                                          title=title, content=content, buttons=buttons,
                                                          notification_id=c.m.sid, questions=questions,
                                                          notification_name=s.notification_name)
            print(message_dict)
            publish_message(s.client_id, s.topic, message_dict)


        to('update_goal').when_all(m.button_type == "ok")

    with stage('update_goal'):
        @run
        def update_goal(c):
            try:
                question_id = c.m.questionnaire_answers[0]["ITEMS"][0]["SELECTED_OPTION_IDS"][0]
                if question_id == 1 or question_id == 2:
                    updated_goal_mets = s.new_goal_mets + s.increase_decrease_values[str(question_id)]
                elif question_id == 4 or question_id == 5:
                    updated_goal_mets = s.new_goal_mets - s.increase_decrease_values[str(question_id)]
                else:
                    updated_goal_mets = s.new_goal_mets

                sql_statement = (f"UPDATE goal SET met_required = {updated_goal_mets} "
                                 f"WHERE user_id = '{s.client_id}' and CURRENT_TIMESTAMP between " 
                                 f"start_date and end_date")
                print(sql_statement)
                db.DbQuery(sql_statement, "insert").create_thread()
                c.delete_state()
            except Exception as e:
                print(e)

with ruleset('notification/morning'):
    @when_all(+m.scheduler_id)
    def get_activity_name(c):
        try:
            s.client_id = c.m.client_id
            s.kwargs = c.m.kwargs
            s.sid = c.m.sid
            s.language_code = c.m.language_code
            sql_statement = f"Select activity_name FROM activity_type WHERE type_id = {c.m.kwargs['activity_type']}"
            activity_name = db.DbQuery(sql_statement, "query_one").create_thread()
            s.activity_name = ld.activity_name[activity_name][c.m.language_code]
            print(s.activity_name)
            c.post({"get_last_session": True})
        except Exception as e:
            print(e)


    @when_all(+m.get_last_session)
    def get_last_session(c):
        try:
            sql_statement = (f"Select feedback FROM task WHERE activity_id IN (SELECT activity_id from "
                             f"activity where user_id = '{s.client_id}') and start_daytime < CURRENT_TIMESTAMP "
                             f"ORDER BY start_daytime DESC LIMIT 1")
            last_session_value = db.DbQuery(sql_statement, "query_one").create_thread()
            c.post({"last_session": last_session_value})
        except Exception as e:
            print(e)


    @when_all(m.last_session == None)
    def get_value_session(c):
        c.post({"value_session": "dq"})


    @when_all(m.last_session == "easy")
    def get_value_session(c):
        c.post({"value_session": "ib"})


    @when_all(m.last_session == "hard")
    def get_value_session(c):
        c.post({"value_session": "db"})


    @when_all(m.last_session == "moderate")
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
            title = query_content[1][0]
            activity_name_message = query_content[2][0].format(s.activity_name, s.kwargs["duration"])
            print(activity_name_message, s.content_msg, met_message)
            content = activity_name_message + s.content_msg + met_message

            button_left = hf.create_buttons_dict(button_type="cancel", content="ignore", language_code=s.language_code)
            button_right = hf.create_buttons_dict(button_type="ok", content="thanks", language_code=s.language_code)
            buttons = [button_right, button_left]
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


    @when_all(+m.button_type)
    def get_feedback(c):
        if c.m.button_type == "ok":
            feedback = 1
        else:
            feedback = 2

        sql_statement = (f"UPDATE notification SET rating = {feedback} "
                         f"WHERE notification_id = '{c.m.sid}'")
        db.DbQuery(sql_statement, "insert").create_thread()
        c.delete_state()

with flowchart('notification/evening'):
    with stage("input"):
        to('first_message').when_all(+m.scheduler_id)

    with stage('first_message'):
        @run
        def create_message(c):
            s.sid = c.m.sid
            s.client_id = c.m.client_id
            s.kwargs = c.m.kwargs
            s.language_code = c.m.language_code
            s.questions = []
            sql_statement = f"Select activity_name FROM activity_type WHERE type_id = {c.m.kwargs['activity_type']}"
            activity_name = db.DbQuery(sql_statement, "query_one").create_thread()
            activity_name = ld.activity_name[activity_name][c.m.language_code]
            sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                             """unnest('{notification_evening_title, 
                             notification_evening_content}'::TEXT[])
                             WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")

            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
            s.title = query_content[0][0].format(activity_name)
            s.content = query_content[1][0]
            button_left = hf.create_buttons_dict(button_type="cancel", content="no", language_code=c.m.language_code,
                                                 wait=True)
            button_right = hf.create_buttons_dict(button_type="ok", content="didit", language_code=c.m.language_code,
                                                  wait=True)
            s.buttons = [button_right, button_left]


        to("send_message")

    with stage('done'):
        @run
        def create_message(c):
            sql_statement = f"UPDATE task SET activity_done='True' WHERE task_id = {s.kwargs['task_id']}"
            db.DbQuery(sql_statement, "insert").create_thread()
            sql_statement = f"Select content{s.language_code} FROM template WHERE daily = 'pos'"
            s.title = db.DbQuery(sql_statement, "query_one").create_thread()
            sql_statement = (
                f"Select content{s.language_code} FROM template WHERE purpose = 'notification_evening_done'")
            s.content = db.DbQuery(sql_statement, "query_one").create_thread()
            button_left = hf.create_buttons_dict(button_type="dislike", content="hard", language_code=s.language_code)
            button_middle = hf.create_buttons_dict(button_type="like", content="right", language_code=s.language_code)
            button_right = hf.create_buttons_dict(button_type="easy", content="easy", language_code=s.language_code)
            s.buttons = [button_right, button_left, button_middle]


        to("send_message")

    with stage('not_done'):
        @run
        def create_message(c):
            sql_statement = (f"Select content{s.language_code} FROM template JOIN "
                             """unnest('{notification_evening_notdone_title, 
                             notification_evening_notdone_content}'::TEXT[])
                             WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""")
            query_content = db.DbQuery(sql_statement, "query_all").create_thread()
            s.title = query_content[0][0]
            s.content = query_content[1][0]
            sql_statement = (f"Select content{s.language_code} FROM template WHERE purpose = "
                             f"'reason'")
            reasons = db.DbQuery(sql_statement, "query_all").create_thread()
            print(reasons)
            item_list = [hf.create_items_dict(
                item_type="single_radio", item_id=1,
                options=[str(i[0]) for i in reasons])
            ]
            s.questions = hf.create_question_dict(content_display=[""], items=[item_list])
            s.buttons = [hf.create_buttons_dict(button_type="next", content="next", language_code=s.language_code, wait=True)]


        to("send_message")

    with stage('insert_difficulty'):
        @run
        def create_message(c):
            s.answer = c.m.button_type
            sql_statement = (f"UPDATE task set feedback = '{s.answer}' WHERE "
                             f" task_id = {s.kwargs['task_id']}")
            print(sql_statement)
            db.DbQuery(sql_statement, "insert").create_thread()


        to("follow_up")

    with stage('insert_reason'):
        @run
        def create_message(c):
            reasons = {"1": "hard",
                       "2": "time",
                       "3": "motivation",
                       "4": "useful"}
            print(c.m.questionnaire_answers)
            s.answer = reasons[str(c.m.questionnaire_answers[0]["ITEMS"][0]["SELECTED_OPTION_IDS"][0])]
            sql_statement = (f"UPDATE task set feedback = '{s.answer}' WHERE "
                             f" task_id = {s.kwargs['task_id']}")
            print(sql_statement)
            db.DbQuery(sql_statement, "insert").create_thread()


        to("follow_up")

    with stage('send_message'):
        @run
        def send_message(c):
            s.notification_name = "notification/evening"
            s.topic = "eu/agewell/event/reasoner/notification/message"
            message_dict = jd.create_notification_message(topic=s.topic, client_id=s.client_id, notification_id=s.sid,
                                                          title=s.title, content=s.content, questions=s.questions,
                                                          buttons=s.buttons,
                                                          notification_name=s.notification_name,
                                                          language=s.language_code)
            print(message_dict)
            publish_message(s.client_id, s.topic, message_dict)


        to('done').when_all(m.button_type == 'ok')
        to('not_done').when_all(m.button_type == 'cancel')
        to('insert_difficulty').when_all(
            (m.button_type == 'easy') | (m.button_type == 'like') | (m.button_type == 'dislike'))
        to('insert_reason').when_all(m.button_type == 'next')

    with stage('follow_up'):
        @run
        def choose_followup_message(c):
            try:
                message_type = {"easy": ["pos", "ia"],
                                "like": ["pos", ""],
                                "dislike": ["pos", "da"],
                                "hard": ["neu", "da"],
                                "time": ["neg", "stg"],
                                "weather": ["neu", ""],
                                "motivation": ["neg", "high"],
                                "useful": ["neg", "low"]}
                type_to_choose = message_type[s.answer]

                sql_queries = [(
                    f"SELECT m.content{s.language_code}, m.template_id from template m where " 
                    f"m.daily = '{type_to_choose[0]}' "
                    f"and NOT EXISTS(SELECT FROM message a WHERE m.template_id = a.template_id AND "
                    f"EXISTS(SELECT from notification s WHERE a.notification_id = s.notification_id and " 
                    f"s.user_id = '{s.client_id}'))"),
                    (
                        f"SELECT template.content{s.language_code}, template.template_id FROM message INNER JOIN "
                        f"template ON message.template_id = "
                        f"template.template_id INNER JOIN notification ON notification.notification_id = "
                        f"message.notification_id WHERE notification.user_id = '{s.client_id}' and notification"
                        f".rating = 1"),
                    (
                        f"select content{s.language_code}, template_id from template where daily = " 
                        f"'{type_to_choose[0]}'")]
                print(sql_queries)
                content_first_msg = db.ChooseMessage(sql_queries, s.sid, s.client_id).choose_right_message()

                if type_to_choose[1] != "":
                    sql_queries = [(
                        f"SELECT m.content{s.language_code}, m.template_id from template m where m.daily = " 
                        f"'{type_to_choose[1]}' "
                        f"and NOT EXISTS(SELECT FROM message a WHERE m.template_id = a.template_id AND "
                        f"EXISTS(SELECT from notification s WHERE a.notification_id = s.notification_id and " 
                        f"s.user_id = '{s.client_id}'))"),
                        (
                            f"SELECT template.content{s.language_code}, template.template_id FROM message INNER JOIN "
                            f"template ON message.template_id = "
                            f"template.template_id INNER JOIN notification ON notification.notification_id = "
                            f"message.notification_id WHERE notification.user_id = '{s.client_id}' and notification"
                            f".rating = 1"),
                        (
                            f"select content{s.language_code}, template_id from template where daily = " 
                            f"'{type_to_choose[1]}'")]
                    content_second_msg = db.ChooseMessage(sql_queries, s.sid, s.client_id).choose_right_message()
                else:
                    content_second_msg = ""
                content = content_first_msg + content_second_msg
                print(content)
                button_left = hf.create_buttons_dict(button_type="cancel", content="ignore", language_code=s.language_code)
                button_right = hf.create_buttons_dict(button_type="ok", content="thanks", language_code=s.language_code)
                buttons = [button_right, button_left]
                message_dict = jd.create_notification_message(topic=s.topic, client_id=s.client_id,
                                                              notification_id=s.sid,
                                                              content=content, buttons=buttons,
                                                              notification_name=s.notification_name,
                                                              language=s.language_code)
                print(message_dict)
                publish_message(s.client_id, s.topic, message_dict)
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
                                 f"WHERE notification_id = '{s.sid}'")
                db.DbQuery(sql_statement, "insert").create_thread()
            except Exception as e:
                print(e)
            c.delete_state()

with flowchart('ipaq/questionnaire'):
    with stage("input"):
        to('first_question').when_all(+m.client_id)

    with stage('first_question'):
        @run
        def create_message(c):
            try:
                print(c.m.sid)
                s.sid = c.m.sid
                s.client_id = c.m.client_id
                s.language_code = c.m.language_code
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_vigorous, 
                                 ipaq_content_vigorous 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                s.title = content[0][0]
                s.content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                s.questions = hf.create_question_dict(content_display=[""], items=[item_list])
                s.buttons = [hf.create_buttons_dict(button_type="next", content="next", wait=True,
                                                    language_code=c.m.language_code)]
            except Exception as e:
                print(e)


        to("send_message")

    with stage('second_question'):
        @run
        def create_message(c):
            try:
                print(c.m.questionnaire_answers)
                s.vigorous_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                      range(2)]
                print(s.vigorous_answers)
                s.sid = c.m.sid
                s.client_id = c.m.client_id
                s.language_code = c.m.language_code
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_moderate, 
                                 ipaq_content_moderate 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                s.title = content[0][0]
                s.content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                s.questions = hf.create_question_dict(content_display=[""], items=[item_list])
                s.buttons = [hf.create_buttons_dict(button_type="next", content="next", wait=True,
                                                    language_code=c.m.language_code)]
            except Exception as e:
                print(e)


        to("send_message_2")

    with stage('third_question'):
        @run
        def create_message(c):
            try:
                s.moderate_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                      range(2)]
                print(s.moderate_answers)
                s.sid = c.m.sid
                s.client_id = c.m.client_id
                s.language_code = c.m.language_code
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 ipaq_title_walking, 
                                 ipaq_content_walking 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                s.title = content[0][0]
                s.content = content[1][0]
                item_list = [hf.create_items_dict(content_display=ld.ipaq["days_content"][c.m.language_code],
                                                  item_type="single_select", item_id=1,
                                                  options=[str(i) for i in range(0, 8)]),
                             hf.create_items_dict(content_display=ld.ipaq["minutes_content"][c.m.language_code],
                                                  item_type="single_select", item_id=2,
                                                  options=[str(i) for i in range(10, 100, 10)])]
                s.questions = hf.create_question_dict(content_display=[""], items=[item_list])
                s.buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                                    language_code=c.m.language_code, wait=True)]
            except Exception as e:
                print(e)


        to("send_message_2")

    with stage('send_message'):
        @run
        def send_message(c):
            questionnaire_type = "ipaq"
            topic = "eu/agewell/event/reasoner/notification/message"
            title = s.title
            notification_name = "ipaq/questionnaire"
            message_dict = jd.create_notification_message(topic=topic, client_id=s.client_id, notification_id=s.sid,
                                                          title=title, content=s.content, questions=s.questions,
                                                          questionnaire_type=questionnaire_type,
                                                          buttons=s.buttons,
                                                          notification_name=notification_name,
                                                          language=s.language_code)
            print(message_dict)
            publish_message(s.client_id, topic, message_dict)


        to('second_question').when_all(m.button_type == 'next')
        to('go_to_mpam').when_all(m.button_type == 'ok')

    with stage('send_message_2'):
        @run
        def send_message(c):
            questionnaire_type = "ipaq"
            topic = "eu/agewell/event/reasoner/notification/message"
            title = s.title
            notification_name = "ipaq/questionnaire"
            message_dict = jd.create_notification_message(topic=topic, client_id=s.client_id, notification_id=s.sid,
                                                          title=title, content=s.content, questions=s.questions,
                                                          questionnaire_type=questionnaire_type,
                                                          buttons=s.buttons,
                                                          notification_name=notification_name,
                                                          language=s.language_code)
            print(message_dict)
            publish_message(s.client_id, topic, message_dict)


        to('third_question').when_all(m.button_type == 'next')
        to('save_answers').when_all(m.button_type == 'ok')

    with stage('save_answers'):
        @run
        def save_answers(c):
            try:
                s.walking_answers = [c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                                     range(2)]
                value = (s.vigorous_answers[0] - 1) * (s.vigorous_answers[1] * 10) * 8 + (s.moderate_answers[0] - 1) * (
                        s.moderate_answers[1] * 10) * \
                        4 + (s.walking_answers[0] - 1) * (s.walking_answers[1] * 10) * 3.3
                sql_statement = (f"UPDATE user_info SET value_ipaq = {value} WHERE "
                                 f"user_id='{s.client_id}'")
                db.DbQuery(sql_statement, "insert").create_thread()
                if value < 500:
                    value = 500
                s.value = value
                sql_statement = f"UPDATE goal SET met_required={value} WHERE user_id='{s.client_id}'"
                db.DbQuery(sql_statement, "insert").create_thread()

            except Exception as e:
                print(e)


        to("show_credits")

    with stage('show_credits'):
        @run
        def show_credits(c):
            try:
                sql_statement = f"Select content{s.language_code} FROM template WHERE purpose='ipaq_credits'"
                content = db.DbQuery(sql_statement, "query_one").create_thread()
                s.title = ""
                s.content = content.format(int(s.value))
                s.buttons = [hf.create_buttons_dict(button_type="ok", content="ok",
                                                    language_code=s.language_code, wait=True)]
                s.questions = []
            except Exception as e:
                print(e)


        to("send_message")

    with stage('go_to_mpam'):
        @run
        def show_credits(c):
            post("mpam/questionnaire", {"sid": s.sid, "client_id": s.client_id, "language_code": s.language_code})
            c.delete_state()

with flowchart('mpam/questionnaire'):
    with stage("input"):
        to('question').when_all(+m.client_id)

    with stage('question'):
        @run
        def create_message(c):
            try:
                s.sid = c.m.sid
                s.client_id = c.m.client_id
                s.language_code = c.m.language_code
                sql_statement = (f"Select content{c.m.language_code} FROM template JOIN "
                                 """unnest('{ 
                                 mpam_title, 
                                 mpam_content 
                                 }'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                 USING (purpose) ORDER  BY t.ord""")
                content = db.DbQuery(sql_statement, "query_all").create_thread()
                s.title = content[0][0]
                s.content = content[1][0]
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
                print(item_list)

                s.questions = hf.create_question_dict(content_display=[""],
                                                      items=[item_list])
                s.buttons = [hf.create_buttons_dict(button_type="ok", content="finish",
                                                    language_code=c.m.language_code)]
            except Exception as e:
                print(e)


        to("send_message")

    with stage('send_message'):
        @run
        def send_message(c):
            questionnaire_type = "mpam"
            topic = "eu/agewell/event/reasoner/notification/message"
            notification_name = "mpam/questionnaire"
            message_dict = jd.create_notification_message(topic=topic, client_id=s.client_id, notification_id=s.sid,
                                                          title=s.title, content=s.content, questions=s.questions,
                                                          questionnaire_type=questionnaire_type,
                                                          buttons=s.buttons,
                                                          notification_name=notification_name,
                                                          language=s.language_code)
            print(message_dict)
            publish_message(s.client_id, topic, message_dict)


        to('save_answers').when_all(m.button_type == 'ok')

    with stage('save_answers'):
        @run
        def save_answers(c):
            try:
                values = str([c.m.questionnaire_answers[0]["ITEMS"][i]["SELECTED_OPTION_IDS"][0] for i in
                              range(len(c.m.questionnaire_answers[0]["ITEMS"]))])
                values = values.replace('[', '{').replace(']', '}').replace('\'', '\"')
                sql_statement = (f"UPDATE user_info SET value_mpam = '{values}' WHERE "
                                 f"user_id='{s.client_id}'")
                db.DbQuery(sql_statement, "insert").create_thread()
                c.delete_state()
            except Exception as e:
                print(e)
