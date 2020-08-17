from configparser import ConfigParser

#Get the configparser object
config_object = ConfigParser()


config_object["Postgres"] = {
    "user": "postgres",
    "password": "vcare",
    "host": "localhost",
    "port": "5433",
    "database": "AgeWell"}


config_object["Scheduler"] = {
    "url": "postgresql+psycopg2://postgres:vcare@localhost:5433/AgeWell",
    "tablename": "apscheduler_jobs"}


config_object["MQTT"] = {
    "user": "agewell-client-01",
    "password": "tolossem2899",
    "host": "dm.agewell-project.eu",
    "port": "8883"}


#Write the above sections to config.ini file
with open('config.ini', 'w') as conf:
    config_object.write(conf)