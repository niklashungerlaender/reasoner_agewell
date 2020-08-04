import logging
import _databasefunctions as db
import _schedule
from _mqttconnection import client_connection

database_login = {"user": "postgres", "password": "vcare", "host": "localhost", "port": "5433",
                  "database": "AgeWell"}


def main():
    db.connect_to_db(database_login["user"], database_login["password"], database_login["host"],
                     database_login["port"], database_login["database"])
    client = client_connection
    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    _schedule.scheduler.start()
    client.loop_forever()


if __name__ == "__main__":
    main()
