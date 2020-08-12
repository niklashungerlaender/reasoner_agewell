from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, date, timedelta
import _databasefunctions as db
import _helperfunctions as hf

jobstores = {
    'default': SQLAlchemyJobStore(url='postgresql+psycopg2://postgres:vcare@localhost:5433/AgeWell',
                                  tablename='apscheduler_jobs')
}
scheduler = BackgroundScheduler(jobstores=jobstores)


class CreateSchedulerJob:
    def __init__(self, runtime, user_id, reminder_id, scheduler_id=None, **kwargs):
        self.runtime = runtime
        self.scheduler_id = scheduler_id
        self.user_id = user_id
        self.karguments = kwargs
        self.reminder_id = reminder_id

    def morning_notification(self):
        self.date_for_scheduler = datetime.combine(self.runtime, hf.get_reminder_time("morning", self.reminder_id))
        self.arguments = ["notification/morning", self.user_id]
        self.create_job()

    def evening_notification(self):
        self.date_for_scheduler = datetime.combine(self.runtime, hf.get_reminder_time("evening", self.reminder_id))
        self.arguments = ["notification/evening", self.user_id]
        self.create_job()

    def create_job(self):
        #self.date_for_scheduler = datetime.now() + timedelta(seconds=5)
        scheduler.add_job(execute_scheduler_job_notification, trigger="date", run_date=self.date_for_scheduler,
                          args=self.arguments, kwargs=self.karguments, id=self.scheduler_id, replace_existing=True)


def execute_scheduler_job_notification(scheduler_event, client_id, scheduler_id=1, **kwargs):
    import _events as ev
    import uuid
    sql_statement = (
        f"SELECT active FROM task WHERE activity_id = (SELECT activity_id from activity where user_id = '{client_id}' "
        f"and type_id = {kwargs['activity_type']} and goal_id = (SELECT s.goal_id from goal s where CURRENT_TIMESTAMP between s.start_date and s.end_date "
        f"and user_id = '{client_id}')) and start_daytime = '{date.today()}'")
    task_active = db.DbQuery(sql_statement, "query_one").create_thread()
    print(task_active)
    if task_active:
        notification_id = uuid.uuid1().int
        sql_statement = (f"INSERT INTO notification(notification_id, user_id, timestamp, rating) VALUES "
                         f"({notification_id},'{client_id}','{datetime.now()}', 0)")
        db.DbQuery(sql_statement, "insert").create_thread()
        sql_statement = f"SELECT language from user_info WHERE user_id = '{client_id}'"
        language_code = db.DbQuery(sql_statement, "query_one").create_thread()
        ev.post(scheduler_event,
                {"sid": notification_id, "client_id": client_id, "scheduler_id": scheduler_id,
                 "language_code": language_code, "kwargs": kwargs})
