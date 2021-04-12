from random import randint
from psycopg2 import pool
from concurrent.futures import ThreadPoolExecutor


# Connection to the database -> Pooling for multiple threads
def connect_to_db(user, password, host, port, database):
    global threaded_postgreSQL_pool
    threaded_postgreSQL_pool = pool.ThreadedConnectionPool(5, 20, user=user,
                                                           password=password,
                                                           host=host,
                                                           port=port,
                                                           database=database)
    if threaded_postgreSQL_pool:
        print("Connection pool created successfully using ThreadedConnectionPool")


class ChooseMessage:
    def __init__(self, sql_queries, notification_id, user_id):
        self.sql1, self.sql2, self.sql3 = sql_queries
        self.notification_id = notification_id
        self.user_id = user_id

    def choose_right_message(self):
        try:
            template_id, content_msg = self.choose_random_message()
            print(template_id, content_msg)
        except IndexError:
            try:
                print("best message")
                template_id, content_msg = self.choose_best_message()
                if not content_msg:
                    print("any message")
                    template_id, content_msg = self.choose_any_message()
            except IndexError:
                print("any message")
                template_id, content_msg = self.choose_any_message()
        sql_statement = (f"INSERT INTO message(notification_id, template_id) VALUES "
                         f"({self.notification_id},{template_id})")
        DbQuery(sql_statement, "insert").create_thread()
        return content_msg

    def choose_random_message(self):
        print("random")
        motivational_message = DbQuery(self.sql1, "query_all").create_thread()
        choose_msg = randint(0, len(motivational_message))
        message_id = motivational_message[choose_msg][1]
        return message_id, motivational_message[choose_msg][0]

    def choose_best_message(self):
        print("best")
        motivational_message = DbQuery(self.sql2, "query_all").create_thread()
        choose_msg = randint(0, len(motivational_message))
        if len(motivational_message) >= 5:
            return motivational_message[choose_msg][1], motivational_message[choose_msg][0]
        else:
            return False, False

    def choose_any_message(self):
        print("any")
        motivational_message = DbQuery(self.sql3, "query_all").create_thread()
        choose_msg = randint(0, len(motivational_message))
        return motivational_message[choose_msg][1], motivational_message[choose_msg][0]


# class db query mit threads pro Abfrage
class DbQuery:
    def __init__(self, sql_statement, type_of_query, fetch=None):
        self.sql_statement = sql_statement
        self.type_of_query = type_of_query
        self.fetch = fetch

    def create_thread(self):
        with ThreadPoolExecutor() as executor:
            query_result = executor.submit(getattr(self, self.type_of_query), self.sql_statement)
            return query_result.result()

    @staticmethod
    def insert(sql_statement):
        ps_connection = None
        try:
            ps_connection = threaded_postgreSQL_pool.getconn()
            with ps_connection:
                ps_cursor = ps_connection.cursor()
                ps_cursor.execute(sql_statement)
                primary_key = 0
                try:
                    primary_key = ps_cursor.fetchone()[0]
                except:
                    pass
                return primary_key
        finally:
            if ps_connection:
                threaded_postgreSQL_pool.putconn(ps_connection)

    @staticmethod
    def query_random(sql_statement):
        ps_connection = None
        try:
            ps_connection = threaded_postgreSQL_pool.getconn()
            with ps_connection:
                ps_cursor = ps_connection.cursor()
                ps_cursor.execute(sql_statement)
                result = ps_cursor.fetchall()
                if len(result) > 1:
                    choose_msg = randint(0, len(result))
                    result = result[choose_msg][1]
                else:
                    result = result[0][0]
                return result
        finally:
            if ps_connection:
                threaded_postgreSQL_pool.putconn(ps_connection)

    @staticmethod
    def query_all(sql_statement):
        ps_connection = None
        try:
            ps_connection = threaded_postgreSQL_pool.getconn()
            with ps_connection:
                ps_cursor = ps_connection.cursor()
                ps_cursor.execute(sql_statement)
                result = ps_cursor.fetchall()
                return result
        finally:
            if ps_connection:
                threaded_postgreSQL_pool.putconn(ps_connection)

    @staticmethod
    def query_one(sql_statement):
        ps_connection = None
        try:
            ps_connection = threaded_postgreSQL_pool.getconn()
            with ps_connection:
                ps_cursor = ps_connection.cursor()
                ps_cursor.execute(sql_statement)
                result = ps_cursor.fetchone()
                result = result[0]
                return result
        except TypeError:
            return None
        finally:
            if ps_connection:
                threaded_postgreSQL_pool.putconn(ps_connection)
