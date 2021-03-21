from datetime import date


def query(key, client_id="", language_code="", run_time="", credits=1000, age=0,
          nickname="", morning_not=0, evening_not=0, notification_name="", activity_id=0, purpose="",
          duration=0, date_task="", gender=None, mot_count = 0, string_to_match = ""):
    dic = dict(get_language=f"SELECT language from user_info WHERE user_id = '{client_id}'",
               update_language=f"UPDATE user_info SET language = '{language_code}' WHERE user_id = '{client_id}'",
               insert_clientid=f"INSERT INTO user_info(user_id) VALUES ('{client_id}') ON CONFLICT DO NOTHING",
               insert_goal=f"INSERT INTO goal(user_id, start_date, end_date, met_required) VALUES "
                           f"('{client_id}','{date.today()}','{run_time}', {credits})",
               insert_activity=f"INSERT INTO activity(user_id, goal_id, type_id) SELECT "
                               f"'{client_id}', (SELECT s.goal_id from goal s where CURRENT_TIMESTAMP between "
                               f"s.start_date and s.end_date "
                               f"and user_id = '{client_id}'), {activity_id} ON CONFLICT DO NOTHING",
               insert_task=f"INSERT INTO task(activity_id, duration, start_daytime, active) SELECT "
                           f"(SELECT activity_id from activity where user_id = '{client_id}' and "
                           f"goal_id = ( "
                           f"SELECT s.goal_id from goal s where "
                           f"CURRENT_TIMESTAMP between s.start_date and s.end_date and user_id = "
                           f"'{client_id}') and type_id = {activity_id}), "
                           f"{int(duration)}, '{date_task}', True  ON CONFLICT ON CONSTRAINT "
                           f"task_activity_id_start_daytime_key DO UPDATE SET active='True', duration= "
                           f"{int(duration)} RETURNING task_id",
               get_number_of_weeks = f"select count(goal_id) from goal where user_id = '{client_id}'",
               get_firstgoal_content=f"Select content{language_code} FROM template JOIN "
                                     """unnest('{first_goal_title, 
                                               first_goal_text}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                                               USING (purpose) ORDER  BY t.ord""",
               get_user_id=f"SELECT user_id from user_info WHERE user_id = '{client_id}'",
               get_gender=f"SELECT gender from user_info WHERE user_id = '{client_id}'",
               update_user_info=f"UPDATE user_info SET age = {age}, "
                                f"nickname = '{nickname}',"
                                f"language = '{language_code}', "
                                f"morning_reminder_id = '{morning_not}', "
                                f"evening_reminder_id = '{evening_not}', "
                                f"gender = '{gender}' "
                                f"WHERE user_id = '{client_id}'",
               update_notification=f"SELECT id, next_run_time from apscheduler_jobs where id LIKE "
                                   f"'{client_id + '%' + notification_name}' ",
               get_activity_types_edit=f"SELECT max(m.type_id), max(m.duration) as duration, ARRAY_AGG(s.start_daytime) "
                                       f"as selected_days, max(s.duration) as selected_duration from activity_type m, task s "
                                       f"WHERE s.active='True' and m.type_id = {int(activity_id)} and s.activity_id = "
                                       f"(SELECT MAX(a.activity_id) from activity a WHERE a.user_id = "
                                       f"'{client_id}' and a.type_id = {int(activity_id)} and a.goal_id = (SELECT c.goal_id from goal c "
                                       f"WHERE CURRENT_TIMESTAMP between c.start_date and c.end_date and "
                                       f"c.user_id = '{client_id}')) GROUP BY m.activity_name",
               get_activity_types_edit_except=f"SELECT max(m.type_id), max(m.duration) as duration, ARRAY_AGG(s.start_daytime) "
                                              f"as selected_days, max(s.duration) as selected_duration from activity_type m, task s "
                                              f"WHERE m.type_id = {int(activity_id)} and s.activity_id = "
                                              f"(SELECT MAX(a.activity_id) from activity a WHERE a.user_id = "
                                              f"'{client_id}' and a.type_id = {int(activity_id)} and a.goal_id = "
                                              f"(SELECT c.goal_id from goal c "
                                              f"WHERE CURRENT_TIMESTAMP between c.start_date and c.end_date and "
                                              f"c.user_id = '{client_id}')) GROUP BY m.activity_name",
               get_activity_infos=f"SELECT s.activity_name, ARRAY_AGG(a.start_daytime), max(a.duration) as duration,"
                                  f"count(CASE WHEN a.activity_done THEN 1 END), max(s.met_value) as met_value, "
                                  f"max(s.type_id), max(s.url), ARRAY_AGG(a.activity_done) from "
                                  f"activity_type s INNER JOIN activity m ON s.type_id = m.type_id "
                                  f"INNER JOIN task a ON a.activity_id = m.activity_id WHERE a.active = 'True' and "
                                  f"m.activity_id IN (SELECT a.activity_id WHERE a.active = 'True') and "
                                  f"m.goal_id = ( "
                                  f"SELECT m.goal_id from goal m where CURRENT_TIMESTAMP between m.start_date "
                                  f"and m.end_date and m.user_id = '{client_id}') GROUP BY s.activity_name",
               get_activities_active_today=f"SELECT s.activity_name FROM activity_type s INNER JOIN activity b ON "
                                           f"s.type_id = b.type_id "
                                           f"INNER JOIN task a ON a.activity_id = b.activity_id "
                                           f"WHERE a.active = 'True' and "
                                           f"a.activity_done IS NULL and a.start_daytime = CURRENT_DATE and "
                                           f"b.goal_id = ( "
                                           f"SELECT m.goal_id from goal m where CURRENT_TIMESTAMP between m.start_date "
                                           f"and m.end_date and m.user_id = '{client_id}')",
               get_activities_done_today=f"SELECT s.activity_name FROM activity_type s INNER JOIN activity b ON "
                                           f"s.type_id = b.type_id "
                                           f"INNER JOIN task a ON a.activity_id = b.activity_id "
                                           f"WHERE a.active = 'True' and "
                                           f"a.activity_done IS True and a.start_daytime = CURRENT_DATE and "
                                           f"b.goal_id = ( "
                                           f"SELECT m.goal_id from goal m where CURRENT_TIMESTAMP between m.start_date "
                                           f"and m.end_date and m.user_id = '{client_id}')",
               get_task_done=f"SELECT start_daytime from task s WHERE activity_done='True' and start_daytime = CURRENT_DATE "
                             f"and s.activity_id = (SELECT MAX(a.activity_id) from activity a WHERE a.user_id = "
                             f"'{client_id}' and a.type_id = {int(activity_id)} and a.goal_id = "
                             f"(SELECT c.goal_id from goal c "
                             f"WHERE CURRENT_TIMESTAMP between c.start_date and c.end_date and "
                             f"c.user_id = '{client_id}')) ORDER BY start_daytime DESC LIMIT 1 ",
               get_goal_id=f"SELECT goal_id from goal WHERE CURRENT_TIMESTAMP between start_date and end_date "
                           f"and user_id = '{client_id}'",
               get_goal_startdate=f"SELECT s.start_date from goal s where user_id = '{client_id}' and s.end_date > "
                                  f"CURRENT_TIMESTAMP",
               get_goal_enddate=f"SELECT s.end_date from goal s where user_id = '{client_id}' and s.end_date > "
                                f"CURRENT_TIMESTAMP",
               get_activity_types=f"SELECT max(m.type_id) as type_id, m.activity_name, max(m.duration) as duration, "
                                  f"ARRAY_AGG(s.content{language_code}) as content, max(m.url) from activity_type m, "
                                  f"template s WHERE m.activity_name = s.activity "
                                  f"and s.category='description' and m.type_id NOT IN (SELECT b.type_id from activity b WHERE b.user_id = "
                                  f"'{client_id}' and b.activity_id in (SELECT s.activity_id FROM task s WHERE "
                                  f"s.active = 'True') and b.goal_id = (SELECT b.goal_id from goal b "
                                  f"WHERE CURRENT_TIMESTAMP between b.start_date and b.end_date and "
                                  f"b.user_id = '{client_id}')) GROUP BY activity_name",
               get_met_value=f"SELECT met_value from activity_type WHERE type_id = {activity_id}",
               get_weekly_mets=f"SELECT met_required from goal where CURRENT_TIMESTAMP between start_date and end_date "
                               f"and user_id = '{client_id}'",
               get_content=f"SELECT content{language_code} FROM template WHERE purpose = '{purpose}'",
               get_links=f"SELECT video{language_code} FROM template WHERE content{language_code} = '{string_to_match}'",
               get_active_mets=f"SELECT b.duration, s.met_value from task b "
                               f"INNER JOIN activity m ON b.activity_id = m.activity_id "
                               f"INNER JOIN activity_type s ON s.type_id = m.type_id "
                               f"WHERE b.active = True and m.activity_id IN "
                               f" (SELECT m.activity_id from activity m WHERE m.goal_id = "
                               f"(SELECT b.goal_id from goal b where CURRENT_TIMESTAMP between b.start_date and "
                               f"b.end_date "
                               f"and user_id = '{client_id}') and m.type_id!={activity_id})",
               get_done_mets=f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                             f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                             f"activity.activity_id WHERE a.active='True' and a.activity_done='True'"
                             f"and a.activity_id IN (SELECT m.activity_id from activity m WHERE m.goal_id = "
                             f"(SELECT b.goal_id from goal b where CURRENT_TIMESTAMP "
                             f"between b.start_date and b.end_date  and user_id = '{client_id}'))",
               get_selected_mets=f"SELECT a.duration, s.met_value from activity_type s INNER JOIN activity "
                                 f"ON s.type_id = activity.type_id JOIN task a ON a.activity_id = "
                                 f"activity.activity_id WHERE a.active='True' and a.activity_id IN (SELECT m.activity_id "
                                 f"from "
                                 f"activity m WHERE m.goal_id = (SELECT b.goal_id from goal b where CURRENT_TIMESTAMP "
                                 f"between b.start_date and b.end_date  and user_id = '{client_id}'))",
               get_morning_not_id=f"Select morning_reminder_id from user_info WHERE user_id='{client_id}'",
               get_evening_not_id=f"Select evening_reminder_id from user_info WHERE user_id='{client_id}'",
               get_task_id=f"SELECT a.task_id FROM activity_type s INNER JOIN activity b ON s.type_id = b.type_id "
                         f"INNER JOIN task a ON a.activity_id = b.activity_id WHERE a.start_daytime = CURRENT_DATE and "
                         f"b.type_id={activity_id} and b.goal_id = ( SELECT m.goal_id from goal m where "
                         f"CURRENT_TIMESTAMP between m.start_date and m.end_date and m.user_id = '{client_id}')",
               update_task=f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from activity where "
                           f"user_id = '{client_id}' "
                           f"and type_id = {activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                           f"CURRENT_TIMESTAMP "
                           f"between s.start_date and s.end_date "
                           f"and user_id = '{client_id}')) and activity_done IS NULL "
                           f"and start_daytime NOT IN {tuple(date_task)}",
               update_task_ifone=f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from "
                                 f"activity where "
                                 f"user_id = '{client_id}' "
                                 f"and type_id = {activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                                 f"CURRENT_TIMESTAMP "
                                 f"between s.start_date and s.end_date "
                                 f"and user_id = '{client_id}')) and activity_done IS NULL "
                                 f"and start_daytime NOT IN ('{date_task}')",
               update_task_ifzero=f"UPDATE task SET active = False WHERE activity_id = (SELECT activity_id from "
                                  f"activity where "
                                  f"user_id = '{client_id}' "
                                  f"and type_id = {activity_id} and goal_id = (SELECT s.goal_id from goal s where "
                                  f"CURRENT_TIMESTAMP "
                                  f"between s.start_date and s.end_date "
                                  f"and user_id = '{client_id}')) and activity_done IS NULL",
               get_dimension_request_content=f"Select content{language_code} FROM template JOIN "
                                             """unnest('{dashboard_title, 
                             dashboard_content}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""",
               get_goalinfo_content=f"Select content{language_code} FROM template JOIN "
                                    """unnest('{goalinfo_info, 
                             goalinfo_achieved, goalinfo_remaining,
                              goalinfo_activities}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""",
               get_goalinfo_content_specific=f"Select content{language_code} FROM template JOIN "
                             """unnest('{goalinfo_activity_days, 
                             goalinfo_activity_info, 
                             goalinfo_activity_achieved, 
                             goalinfo_activity_completed}'::TEXT[]) WITH ORDINALITY t(purpose, ord)
                             USING (purpose) ORDER  BY t.ord""",
               get_missed_days = f"SELECT s.activity_name from activity_type s INNER JOIN activity m ON "
                                 f"s.type_id = m.type_id INNER JOIN task a ON a.activity_id = m.activity_id "
                                 f"WHERE a.activity_done is NULL and a.active = 'True' and a.start_daytime < "
                                 f"CURRENT_DATE and m.activity_id IN (SELECT m.activity_id from activity m WHERE "
                                 f"m.user_id = '{client_id}' and m.goal_id = "
                                 f"(SELECT c.goal_id from goal c WHERE CURRENT_TIMESTAMP between c.start_date and "
                                 f"c.end_date and c.user_id = '{client_id}'))",
               delete_missed_days=f"UPDATE task SET active = False WHERE activity_id IN (SELECT activity_id from "
                                  f"activity where "
                                  f"user_id = '{client_id}' and goal_id = (SELECT s.goal_id from goal s where "
                                  f"CURRENT_TIMESTAMP between s.start_date and s.end_date and user_id = "
                                  f"'{client_id}')) and activity_done IS NULL and start_daytime < current_date",
               get_nickname= f"SELECT nickname from user_info WHERE user_id = '{client_id}'",
               get_motivational_messages = [(
                    f"SELECT m.content{language_code}, m.template_id from template m where "
                    f"m.daily = '{purpose}' "
                    f"and NOT EXISTS(SELECT FROM message a WHERE m.template_id = a.template_id AND "
                    f"EXISTS(SELECT from notification s WHERE a.notification_id = s.notification_id and "
                    f"s.user_id = '{client_id}'))"),
                    (
                        f"SELECT template.content{language_code}, template.template_id FROM message INNER JOIN "
                        f"template ON message.template_id = "
                        f"template.template_id INNER JOIN notification ON notification.notification_id = "
                        f"message.notification_id WHERE notification.user_id = '{client_id}' and notification"
                        f".rating = 1"),
                    (
                        f"select content{language_code}, template_id from template where daily = "
                        f"'{purpose}'")],
               get_motivational_messages_alternative = [(
                        f"SELECT m.content{language_code}, m.template_id from template m where m.daily = "
                        f"'{purpose}' "
                        f"and NOT EXISTS(SELECT FROM message a WHERE m.template_id = a.template_id AND "
                        f"EXISTS(SELECT from notification s WHERE a.notification_id = s.notification_id and "
                        f"s.user_id = '{client_id}'))"),
                        (
                            f"SELECT template.content{language_code}, template.template_id FROM message INNER JOIN "
                            f"template ON message.template_id = "
                            f"template.template_id INNER JOIN notification ON notification.notification_id = "
                            f"message.notification_id WHERE notification.user_id = '{client_id}' and notification"
                            f".rating = 1"),
                        (
                            f"select content{language_code}, template_id from template where daily = "
                            f"'{purpose}'")],
               get_motivation_count = f"select count_motivation_message from user_info where user_id ='{client_id}'",
               insert_message_count = f"UPDATE user_info SET count_motivation_message = {mot_count} WHERE user_id = " 
                                      f"'{client_id}'",
               motivational_content = f"SELECT content{language_code} from template where purpose = 'mot_morning' and "
                                      f"template_id = (Select count_motivation_message from user_info where user_id = " 
                                      f"'{client_id}')",
               motivational_content_random=f"SELECT content{language_code} from template where purpose = 'mot_morning'"


               )

    return dic[key]
