from collections import defaultdict
from random import randint
import _languagedicts as ld


def get_content(i, pos_t, pos_c):
    res = defaultdict(list)
    for title, content in zip(i[pos_t], i[pos_c]):
        res[title].append(content)
    rest = "".join(
        str(key.capitalize()) + ": " + str(value[randint(0, len(value) - 1)] + " ") for key, value in res.items())
    return rest


def create_notification_message(topic="", client_id="", notification_id=1,
                                title="", content="", questions=[],
                                buttons=[], instance_id="", notification_name="",
                                questionnaire_type="", language=""):
    notification_dict = {"topic": topic, "properties": {}}
    notification_dict["properties"]["CLIENT_ID"] = client_id
    notification_dict["properties"]["DIMENSION_ID"] = 1
    notification_dict["properties"]["LANGUAGE_CODE"] = language
    notification_dict["properties"]["TITLE_DISPLAY"] = title
    notification_dict["properties"]["TITLE_TEXT_TO_SPEECH"] = title
    notification_dict["properties"]["CONTENT_DISPLAY"] = content
    notification_dict["properties"]["CONTENT_TEXT_TO_SPEECH"] = content
    notification_dict["properties"]["NOTIFICATION_ID"] = str(notification_id)
    notification_dict["properties"]["QUESTIONNAIRE_TYPE"] = questionnaire_type
    notification_dict["properties"]["QUESTIONS"] = questions
    notification_dict["properties"]["BUTTONS"] = buttons
    notification_dict["properties"]["FIREBASE_INSTANCE_ID"] = instance_id
    notification_dict["properties"]["NOTIFICATION_NAME"] = notification_name

    return notification_dict


def create_credits_information_response(topic="", client_id="", text="", language=""):
    notification_dict = {"topic": topic, "properties": {}}
    notification_dict["properties"]["CLIENT_ID"] = client_id
    notification_dict["properties"]["LANGUAGE_CODE"] = language
    notification_dict["properties"]["CONTENT_DISPLAY"] = text

    return notification_dict


def create_activity_types_edit_message(topic="", activity_id="", client_id="", duration=[], selected_duration=[],
                                       days=[], selected_days=[], language=""):
    try:
        notification_dict = {"topic": topic, "properties": {}}
        notification_dict["properties"]["CLIENT_ID"] = client_id
        notification_dict["properties"]["DIMENSION_ID"] = 1
        notification_dict["properties"]["LANGUAGE_CODE"] = language
        notification_dict["properties"]["ACTIVITY_ID"] = activity_id
        notification_dict["properties"]["DAYS"] = days
        notification_dict["properties"]["DURATION"] = duration
        notification_dict["properties"]["SELECTED_DAYS"] = selected_days
        notification_dict["properties"]["SELECTED_DURATION"] = selected_duration

        return notification_dict
    except Exception as e:
        print(e)


def create_activity_types_message(topic="", client_id="", types="",
                                  days="", language=""):
    try:
        types_list = [
            {"ID": i[0], "TITLE_DISPLAY": ld.activity_name[i[1]][language], "DAYS": days, "DURATION": i[2],
             "CONTENT_DISPLAY": get_content(i, 4, 3), "CONTENT_IMAGE": i[5]}
            for i in types
        ]
        notification_dict = {"topic": topic, "properties": {}}
        notification_dict["properties"]["CLIENT_ID"] = client_id
        notification_dict["properties"]["DIMENSION_ID"] = 1
        notification_dict["properties"]["LANGUAGE_CODE"] = language
        notification_dict["properties"]["TYPES"] = types_list
        return notification_dict
    except Exception as e:
        print(e)


def create_dimension_notification(topic="", client_id="", title="",
                                  title_short="", text="", progress="", language=""):
    notification_dict = {"topic": topic, "properties": {}}
    notification_dict["properties"]["CLIENT_ID"] = client_id
    notification_dict["properties"]["LANGUAGE_CODE"] = language
    notification_dict["properties"]["DIMENSION"] = [{}]
    notification_dict["properties"]["DIMENSION"][0]["ID"] = 1
    notification_dict["properties"]["DIMENSION"][0]["TITLE_DISPLAY"] = title
    notification_dict["properties"]["DIMENSION"][0]["TITLE_DISPLAY_SHORT"] = title_short
    notification_dict["properties"]["DIMENSION"][0]["CONTENT_DISPLAY"] = text
    notification_dict["properties"]["DIMENSION"][0]["PROGRESS"] = progress

    return notification_dict


def create_useractivity_notification(topic="", client_id="", goal_credits="",
                                     goal_content_display="", language="",
                                     activities_list=""):
    notification_dict = {"topic": topic, "properties": {}}
    notification_dict["properties"]["CLIENT_ID"] = client_id
    notification_dict["properties"]["DIMENSION_ID"] = 1
    notification_dict["properties"]["GOAL_CREDITS"] = goal_credits
    notification_dict["properties"]["CONTENT_DISPLAY"] = goal_content_display
    notification_dict["properties"]["CONTENT_IMAGE"] = "https://proself.org/storage/images/ait/goal.jpg"
    notification_dict["properties"]["LANGUAGE_CODE"] = language
    notification_dict["properties"]["ACTIVITIES"] = activities_list

    return notification_dict
