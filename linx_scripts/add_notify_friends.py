import sqlite3
import requests
import datetime
import json
from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError


# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
        print("succeeded")
    except PushServerError as exc:
        print("issue1")
        print("{} ||| {} ||| {} ||| {}".format(message, extra, exc.errors, exc.response_data))
        # Encountered some likely formatting/validation error.
       # rollbar.report_exc_info(
       #     extra_data={
       #         'token': token,
       #         'message': message,
       #         'extra': extra,
       #         'errors': exc.errors,
       #         'response_data': exc.response_data,
       #     })
        raise
    except (ConnectionError, HTTPError) as exc:
        print("issue2")
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
#        rollbar.report_exc_info(
#            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
        print("succeeded2")
    except DeviceNotRegisteredError:
        print("error3")
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc:
        # Encountered some other per-notification error.
        print("error")
#        rollbar.report_exc_info(
#            extra_data={
#                'token': token,
#                'message': message,
#                'extra': extra,
#                'push_response': exc.push_response._asdict(),
#            })
        raise self.retry(exc=exc)



sql_connect = sqlite3.connect('/home/ubuntu/linx-backend-python-django/linx/db.sqlite3')
cursor = sql_connect.cursor()

# Search for friends that are compatible
query = "SELECT DISTINCT a.iid as image_id, a.user_id as a_user, b.user_id as b_user FROM linx_reactions as a INNER JOIN linx_reactions as b ON a.iid = b.iid WHERE a.reaction_type = b.reaction_type AND a.user_id != b.user_id;"
reaction_results = cursor.execute(query).fetchall()
query = "SELECT user_id, friends, info, last_friend_added FROM linx_luser;"
friends_results = cursor.execute(query).fetchall()
sql_connect.close()

reaction_map = {}
for row in reaction_results:
    if reaction_map.get(row[1]) == None:
        reaction_map[row[1]] = {}
        reaction_map[row[1]][row[2]] = 1
    else:
        if reaction_map[row[1]].get(row[2]) == None:
            reaction_map[row[1]][row[2]] = 1
        else:
            reaction_map[row[1]][row[2]] += 1

friends_to_match = []
for user in reaction_map:
    for matching_user in reaction_map[user]:
        if reaction_map[user][matching_user] > 4:
            friend_combo = (user, matching_user)
            if friend_combo not in friends_to_match:
                friends_to_match.append(friend_combo)

user_to_friends_to_change = {}
for row in friends_results:
    # create dictionary of user_id to list
    user_to_friends_to_change[str(row[0])] = row[1].strip('][').split(',')

final_modifcations = {}

print(friends_to_match)
print("ll")
print(user_to_friends_to_change)
for item in friends_to_match:
    print(item)
    # If one is none they are both none seeing as we adding 2 at a time
    if item[1] not in user_to_friends_to_change[item[0]]:
        if final_modifcations.get(item[0]) == None:
            user_to_friends_to_change[item[0]] = []
            user_to_friends_to_change[item[0]].append(item[1])
            final_modifcations[item[0]] = user_to_friends_to_change[item[0]]
            user_to_friends_to_change[item[1]] = []
            user_to_friends_to_change[item[1]].append(item[0])
            final_modifcations[item[1]] = user_to_friends_to_change[item[1]]
        else:
            pass
           # Commenting out becasue only 1 should be added
           # final_modifcations[item[0]].append(item[1])
           # final_modifcations[item[0]] = final_modifcations[item[0]]
           # final_modifcations[item[1]].append(item[0])
           # final_modifcations[item[1]] = final_modifcations[item[1]]

print(final_modifcations)
print("About to execute commands")
sql_connect = sqlite3.connect('/Users/sam/Projects/linx-backend-python-django/linx/db.sqlite3')
cursor = sql_connect.cursor()


for item in final_modifcations:
    loaded_info = json.loads(friends_results[item][2])
    last_reaction_time = datetime.datetime.now() - loaded_info["lastReaction"]
    friend_time_elapsed = datetime.datetime.now() - friends_results[item][3]
    if last_reaction_time.days < 2 and friend_time_elapsed.days > 1:
        query = "UPDATE linx_luser SET friends=\'{}\' last_friend_added={} WHERE user_id = {}".format(final_modifcations[item], datetime.datetime.now(), item)
        cursor.execute(query)

sql_connect.close()

for index in final_modifcations:
    loaded_info = json.loads(friends_results[index][2])
    expo_push_token = loaded_info["expoPushToken"]
    data = {"user_id": "{}".format(item),
         "timestamp": datetime.datetime.now(),
         "type": "friends"
         }
    send_push_message(expo_push_token, "You have a new friend!", data) 