from collections import defaultdict
from random import randint
import _languagedicts as ld
import _helperfunctions as hf


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
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["DIMENSION_ID"] = 1
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["TITLE_DISPLAY"] = title
    nd["properties"]["TITLE_TEXT_TO_SPEECH"] = title
    nd["properties"]["CONTENT_DISPLAY"] = hf.string_formatting(content)
    nd["properties"]["CONTENT_TEXT_TO_SPEECH"] = hf.string_formatting(content)
    nd["properties"]["NOTIFICATION_ID"] = str(notification_id)
    nd["properties"]["QUESTIONNAIRE_TYPE"] = questionnaire_type
    nd["properties"]["QUESTIONS"] = questions
    nd["properties"]["BUTTONS"] = buttons
    nd["properties"]["FIREBASE_INSTANCE_ID"] = instance_id
    nd["properties"]["NOTIFICATION_NAME"] = notification_name

    return nd


def create_credits_information_response(topic="", client_id="", text="", language=""):
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["CONTENT_DISPLAY"] = hf.string_formatting(text)

    return nd


def create_activity_types_edit_message(topic="", activity_id="", client_id="", duration=[], selected_duration=[],
                                       days=[], selected_days=[], language=""):
    try:
        nd = {"topic": topic, "properties": {}}
        nd["properties"]["CLIENT_ID"] = client_id
        nd["properties"]["DIMENSION_ID"] = 1
        nd["properties"]["LANGUAGE_CODE"] = language
        nd["properties"]["ACTIVITY_ID"] = activity_id
        nd["properties"]["DAYS"] = days
        nd["properties"]["DURATION"] = duration
        nd["properties"]["SELECTED_DAYS"] = selected_days
        nd["properties"]["SELECTED_DURATION"] = selected_duration

        return nd
    except Exception as e:
        print(e)


def create_activity_types_message(topic="", client_id="", types="",
                                  days="", language=""):
    try:
        types_list = [
            {"ID": i[0], "TITLE_DISPLAY": ld.activity_name[i[1]][language], "DAYS": days, "DURATION": i[2],
             "CONTENT_DISPLAY": hf.string_formatting(get_content(i, 4, 3)), "CONTENT_IMAGE": i[5]}
            for i in types
        ]
        nd = {"topic": topic, "properties": {}}
        nd["properties"]["CLIENT_ID"] = client_id
        nd["properties"]["DIMENSION_ID"] = 1
        nd["properties"]["LANGUAGE_CODE"] = language
        nd["properties"]["TYPES"] = types_list
        return nd
    except Exception as e:
        print(e)


def create_dimension_notification(topic="", client_id="", title="",
                                  title_short="", text="", progress="", language=""):
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["DIMENSION"] = [{}]
    nd["properties"]["DIMENSION"][0]["ID"] = 1
    nd["properties"]["DIMENSION"][0]["TITLE_DISPLAY"] = title
    nd["properties"]["DIMENSION"][0]["TITLE_DISPLAY_SHORT"] = title_short
    nd["properties"]["DIMENSION"][0]["CONTENT_DISPLAY"] = hf.string_formatting(text)
    nd["properties"]["DIMENSION"][0]["PROGRESS"] = progress

    return nd


def create_useractivity_notification(topic="", client_id="", goal_credits="",
                                     goal_content_display="", language="",
                                     activities_list=""):
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["DIMENSION_ID"] = 1
    nd["properties"]["GOAL_CREDITS"] = goal_credits
    nd["properties"]["CONTENT_DISPLAY"] = hf.string_formatting(goal_content_display)
    nd["properties"]["CONTENT_IMAGE"] = "https://proself.org/storage/images/ait/goal.jpg"
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["ACTIVITIES"] = activities_list

    return nd
