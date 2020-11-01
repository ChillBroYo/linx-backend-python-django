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
        raise
    except (ConnectionError, HTTPError) as exc:
        print("issue2")
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
        raise self.retry(exc=exc)

db_location = 'db.sqlite3'
#db_location = '/home/ubuntu/linx-backend-python-django/linx/db.sqlite3'
sql_connect = sqlite3.connect(db_location)
cursor = sql_connect.cursor()
ids_to_notify = {}

class UserObj:
    def __init__(self, user_id, expo_push_token, first_name):
        self.user_id = user_id
        self.expo_push_token = expo_push_token
        self.first_name = first_name

# Get user info
query = "SELECT user_id, json_extract(linx_luser.info, '$.expoPushToken'), json_extract(linx_luser.info, '$.name.first') from linx_luser ORDER BY user_id;"
user_id_query = cursor.execute(query).fetchall()

# Build user mapping
user_map = {}
for item in user_id_query:
    new_user_info = UserObj(item[0], item[1], item[2])
    user_map[int(new_user_info.user_id)] = new_user_info

class MessageObj:
    def __init__(self, message_id, user_sent_from, user_to_recieve, time_user_seen, users_notified):
        self.message_id = message_id
        self.user_sent_from = user_sent_from
        self.user_to_recieve = user_to_recieve
        self.time_user_seen = time_user_seen
        self.users_notified = users_notified


# Get all messages new messages
query = "SELECT mid, user_id, other_id, time_user_seen, users_notified FROM linx_messages WHERE users_notified != 'true'"
messages_query = cursor.execute(query).fetchall()

# Go through each message not notified and message users
for message in messages_query:

    # Escape out if there are no exisitent ids or the user doesn't exist anymore
    if message[1] == None or message[2] == None or message[1] == '' or message[2] == '':
        continue
    else:
        in_set = 0
        for user_id in user_map:
            if int(message[1]) == int(user_id):
                in_set += 1
            elif int(message[2]) == int(user_id):
                in_set += 1
        if in_set != 2:
            continue

    msg = MessageObj(message[0], message[1], message[2], message[3], message[4])

    # If theres a message to be notified, add the other user id to the mapping, and add the message it was sent from, unique to each user id
    if ids_to_notify.get(msg.user_to_recieve) == None:
        ids_to_notify[msg.user_to_recieve] = [msg.user_sent_from]
    elif msg.user_sent_from not in ids_to_notify[msg.user_to_recieve]:
        ids_to_notify[msg.user_to_recieve].append(msg.user_sent_from)
    
    # Update message to say its been delivered
    update_query = "UPDATE linx_messages SET time_user_seen = \'{}\', users_notified = \'{}\' WHERE mid = {}".format(datetime.datetime.now(), "true", msg.message_id)
    sql_connect = sqlite3.connect(db_location)
    cursor = sql_connect.cursor()
    cursor.execute(update_query)
    sql_connect.commit()
    sql_connect.close()


print("At {} sent notifications to users {}".format(datetime.datetime.now(), ids_to_notify))
sql_connect.close()
for user_id in ids_to_notify:
    if not hasattr(user_map[int(user_id)], 'expo_push_token'):
        print("Skipped sending messages to user {} due to missing push token".format(user_map[user_id].user_id))
        continue
    for message_recieved_from_id in ids_to_notify[user_id]:
        print("Sending message to {} about {}".format(user_id, message_recieved_from_id))
        message_to_send = "You have a new message from {}".format(user_map[int(message_recieved_from_id)].first_name)
        data = {"user_id": "{}".format(user_map[int(user_id)].user_id),
             "timestamp": str(datetime.datetime.now()),
             "type": "message"
            }
        send_push_message(user_map[int(user_id)].expo_push_token, message_to_send, data) 
