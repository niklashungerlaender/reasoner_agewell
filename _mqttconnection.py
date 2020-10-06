import paho.mqtt.client as mqtt
import json
import re
import _helperfunctions as hf
from configparser import ConfigParser


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqtt_topic + "/+/eu/agewell/event/reasoner/#")
    client.subscribe(mqtt_topic + "/+/at/ac/ait/hbs/dialog/client/#")
    client.subscribe("eu/" + mqtt_topic + "/event/reasoner/#")


# The callback for when a PUBLISH message is received from the server.

def on_message(client, userdata, msg):
    import _events
    try:
        message = json.loads(msg.payload)
        print (message)
        topic = parse_topic(msg.topic)
        message_content = dict((k.lower(), v) for k, v in message["properties"].items())
        """
        try:
            message_content["preferences"].update({"language_code":"en"})
        except:
            message_content.update({"language_code":"en"})
        """
        print(topic, message_content)
        try:
            _events.post(topic, message_content)
        except Exception as e:
            print(e)
            pass
    except Exception as e:
        print(e)


def parse_topic(message):
    try:
        regexp_topic = re.compile("(reasoner/(.*))")
        topic = regexp_topic.search(message).group(2)
    except:
        regexp_topic = re.compile("(client/(.*))")
        topic = regexp_topic.search(message).group(2)
    return topic


def connect_to_mqtt(username, password, host, port):
    client_conn = mqtt.Client()
    client_conn.tls_set_context(context=None)
    client_conn.username_pw_set(username=username, password=password)
    client_conn.on_connect = on_connect
    client_conn.on_message = on_message
    client_conn.connect(host, port)
    return client_conn


def publish_message(client_id, topic, message):
    try:
        prefix = f"{mqtt_topic}/{client_id}/"
        topic = prefix + topic
        message = json.dumps(message)
        client_connection.publish(topic, message)
        print (topic)
    except Exception as e:
        print(e, "publish")


config_object = ConfigParser()
config_object.read("config.ini")
mqtt_login = config_object["MQTT"]
mqtt_topic = mqtt_login["topic"]
client_connection = connect_to_mqtt(mqtt_login["user"], mqtt_login["password"], mqtt_login["host"],
                                    int(mqtt_login["port"]))