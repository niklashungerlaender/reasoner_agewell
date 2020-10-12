import psycopg2
from configparser import ConfigParser


def connect_to_db():
    try:
        config_object = ConfigParser()
        config_object.read("config.ini")
        database_login = config_object["Postgres"]
        connection = psycopg2.connect(user = database_login["user"],
                                      password = database_login["password"],
                                      host = database_login["host"],
                                      port = database_login["port"],
                                      database = database_login["database"])

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")

        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
        return connection, cursor

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)


def create_tables(connection, cursor):
    commands = (
        """
        CREATE TABLE user_info (
            user_id TEXT PRIMARY KEY,
            age SMALLINT,
            value_mpam integer[],
            value_ipaq SMALLINT,
            morning_reminder_id SMALLINT,
            evening_reminder_id SMALLINT, 
            gender VARCHAR(255),
            firebaseInstanceId VARCHAR(255),
            userIdOAuth VARCHAR(255),
            nickname VARCHAR(255),
            language VARCHAR(255),
            mqttUser VARCHAR(255)


        )
        """,
        """ CREATE TABLE template (
                template_id SERIAL PRIMARY KEY,
                contenten TEXT NOT NULL,
                contentde TEXT, 
                contentit TEXT,
                contentnl TEXT,
                pam TEXT,
                mpam SMALLINT,
                weekly TEXT,
                daily TEXT,
                difficulty TEXT,
                purpose TEXT,
                activity TEXT,
                category TEXT
                )
        """,
        """ CREATE TABLE notification (
                notification_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES user_info (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                timestamp TIMESTAMP NOT NULL,
                rating SMALLINT
                )
        """,
        """ CREATE TABLE message (
                template_id SERIAL NOT NULL,
                FOREIGN KEY (template_id)
                    REFERENCES template (template_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                notification_id TEXT NOT NULL,
                FOREIGN KEY (notification_id)
                    REFERENCES notification (notification_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                PRIMARY KEY(template_id, notification_id)
                )
        """,
        """
        CREATE TABLE activity_type(
                type_id SERIAL PRIMARY KEY,
                activity_name VARCHAR(255) NOT NULL,
                met_value SMALLINT NOT NULL,
                duration integer[],
                url text,
                UNIQUE (activity_name)
        )
        """,
        """
        CREATE TABLE goal(
                goal_id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                FOREIGN KEY (user_id)
                    REFERENCES user_Info (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                met_required SMALLINT,
                achieved SMALLINT
        )
        """,
        """
        CREATE TABLE activity(
                activity_id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                goal_id SMALLINT NOT NULL,
                type_id SMALLINT NOT NULL,
                FOREIGN KEY (type_id)
                    REFERENCES activity_type (type_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (user_id)
                    REFERENCES user_info (user_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (goal_id)
                    REFERENCES goal (goal_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                UNIQUE (goal_id, user_id, type_id)
        )
        """,
        """
        CREATE TABLE task(
                task_id SERIAL PRIMARY KEY,
                activity_id SMALLINT,
                FOREIGN KEY (activity_id)
                    REFERENCES activity (activity_id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                feedback VARCHAR(255),
                duration SMALLINT,
                start_daytime TIMESTAMP,
                activity_done BOOLEAN,
                active BOOLEAN,
                UNIQUE (activity_id, start_daytime)
        )
        """,

    )
    try:
        for command in commands:
            cursor.execute(command)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_activities(connection, cursor):
    activities = {"cycling": (6, [20, 30, 40, 50], "https://proself.org/storage/images/ait/cycling.jpg"),
                         "walking": (3, [30, 40, 50, 60], "https://proself.org/storage/images/ait/walking.jpg"),
                         "shoveling": (6, [10, 20, 30], "https://proself.org/storage/images/ait/shoveling.jpg"),
                         "yoga": (3, [10, 20, 30, 40], "https://proself.org/storage/images/ait/yoga.jpg"),
                         "strength": (6, [20, 30, 40, 50], "https://proself.org/storage/images/ait/strenght.jpg")}
    for k, v in activities.items():
        try:
            cursor.execute(
                """insert into activity_type (activity_name, met_value, duration, url) VALUES (%s, %s, %s, %s)""",
                [k, v[0], v[1], v[2]])
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    connection.commit()


def insert_templates(connection, cursor):
    with open('motivational_messages.csv', 'r') as f:
        next(f) # Skip the header row.
        cursor.copy_from(f, 'template', sep=';')
    connection.commit()


def main():
    connection, cursor = connect_to_db()
    #create_tables(connection,cursor)
    #insert_activities(connection, cursor)
    insert_templates(connection, cursor)
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()