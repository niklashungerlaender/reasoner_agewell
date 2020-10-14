import _languagedicts as ld
import _helperfunctions as hf

"""
def get_content(i, pos_t, pos_c, language):
    res = defaultdict(list)
    for title, content in zip(i[pos_t], i[pos_c]):
        res[ld.content_title[title][language]].append(content)
    rest = "".join(
        str(key.capitalize()) + ": " + str(value[randint(0, len(value) - 1)] + " ") for key, value in res.items())
    return rest
"""


def create_notification_message(topic="", client_id="", notification_id=1,
                                title="", content="", questions=[],
                                buttons=[], instance_id="", notification_name="",
                                questionnaire_type="", language=""):
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["DIMENSION_ID"] = 1
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["TITLE_DISPLAY"] = hf.string_formatting(title)
    nd["properties"]["TITLE_TEXT_TO_SPEECH"] = hf.string_formatting(title)
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


def create_activity_types_edit_response(topic="", activity_id="", client_id="", duration=[], selected_duration=[],
                                       days=[], selected_days=[], language="", content_display_sub_screens=[]):
    try:
        content_sub_screens = [{"ID": i[0], "CONTENT_DISPLAY": hf.string_formatting(i[1]),
                                "CONTENT_TEXT_TO_SPEECH": i[2]}
                               for i in content_display_sub_screens]
        nd = {"topic": topic, "properties": {}}
        nd["properties"]["CLIENT_ID"] = client_id
        nd["properties"]["DIMENSION_ID"] = 1
        nd["properties"]["LANGUAGE_CODE"] = language
        nd["properties"]["ACTIVITY_ID"] = activity_id
        nd["properties"]["DAYS"] = days
        nd["properties"]["DURATION"] = [
                {"VALUE":j, "CONTENT_DISPLAY": j + " " + ld.minutes[language]} for j in duration]
        nd["properties"]["SELECTED_DAYS"] = selected_days
        nd["properties"]["SELECTED_DURATION"] = selected_duration
        nd["properties"]["SUB_SCREENS"] = content_sub_screens

        return nd
    except Exception as e:
        print(e)


def create_activity_types_response(topic="", client_id="", types="",
                                  days="", language="", content_display_sub_screens = []):
    try:
        types_list = [
            {"ID": i[0], "TITLE_DISPLAY": ld.activity_name[i[1]][language], "DAYS": days, "DURATION": [
                {"VALUE":str(j), "CONTENT_DISPLAY": str(j) + " " + ld.minutes[language]} for j in i[2]],
             "CONTENT_DISPLAY": i[3], "CONTENT_IMAGE": i[4]}
            for i in types
        ]
        content_sub_screens = [{"ID":i[0], "CONTENT_DISPLAY": hf.string_formatting(i[1]),
                               "CONTENT_TEXT_TO_SPEECH": i[2]}
                               for i in content_display_sub_screens]
        nd = {"topic": topic, "properties": {}}
        nd["properties"]["CLIENT_ID"] = client_id
        nd["properties"]["DIMENSION_ID"] = 1
        nd["properties"]["LANGUAGE_CODE"] = language
        nd["properties"]["TYPES"] = types_list
        nd["properties"]["SUB_SCREENS"] = content_sub_screens
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


def create_user_activity_response(topic="", client_id="", goal_credits="",
                                     content_display_sub="", language="",
                                     activities_list="", title_display = "",
                                     text_to_speech_sub="", text_to_speech_main="",
                                  title_display_sub=""):
    content_sub_screens = [{"ID": "goal_info", "CONTENT_DISPLAY":hf.string_formatting(content_display_sub),
                           "CONTENT_TEXT_TO_SPEECH":text_to_speech_sub, "TITLE_DISPLAY":title_display_sub}]
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["DIMENSION_ID"] = 1
    nd["properties"]["TITLE_DISPLAY"] = title_display
    nd["properties"]["GOAL_CREDITS"] = goal_credits
    nd["properties"]["CONTENT_IMAGE"] = "https://proself.org/storage/images/ait/goal.jpg"
    nd["properties"]["LANGUAGE_CODE"] = language
    nd["properties"]["ACTIVITIES"] = activities_list
    nd["properties"]["SUB_SCREENS"] = content_sub_screens
    nd["properties"]["CONTENT_TEXT_TO_SPEECH"] = text_to_speech_main

    return nd


def create_useractivity_response(topic="", client_id="", activity_id=""):
    nd = {"topic": topic, "properties": {}}
    nd["properties"]["CLIENT_ID"] = client_id
    nd["properties"]["DIMENSION_ID"] = 1
    nd["properties"]["ACTIVITY_ID"] = activity_id

    return nd