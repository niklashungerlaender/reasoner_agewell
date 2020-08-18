import logging
import _databasefunctions as db
import _schedule
from _mqttconnection import client_connection
from configparser import ConfigParser


def main():
    config_object = ConfigParser()
    config_object.read("config.ini")
    database_login = config_object["Postgres"]
    mqtt_login = config_object["MQTT"]
    db.connect_to_db(database_login["user"], database_login["password"], database_login["host"],
                     database_login["port"], database_login["database"])
    client = client_connection
    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    _schedule.scheduler.start()
    client.loop_forever()


if __name__ == "__main__":
    main()
