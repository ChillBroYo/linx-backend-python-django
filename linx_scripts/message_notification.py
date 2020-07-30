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
user_ids = []
# Search for friends that are compatible
query = "SELECT user_id, info from linx_luser ORDER BY user_id;"
user_id_query = cursor.execute(query).fetchall()
for row in user_id_query:
    query = "SELECT COUNT(mid) FROM linx_messages WHERE user_id = {} AND (time_user_seen == NULL OR users_notified='false');".format(row[0])
    count_query = cursor.execute(query).fetchall()
    if int(count_query[0][0]) > 0:
        user_ids.append(row[0])
        "ALTER TABLE linx_messages SET time_user_seen=\'{}\', users_notified=\'true\' WHERE user_id={}".format(datetime.datetime.now(), row[0])
        count_query = cursor.execute(query)

sql_connect.close()

for user_id in user_ids:
    loaded_info = json.loads(user_id_query[user_id][1])
    expo_push_token = loaded_info["expoPushToken"]
    data = {"user_id": "{}".format(user_id),
         "timestamp": datetime.datetime.now(),
         "type": "message"
         }
    send_push_message(expo_push_token, "You have a new message", data) 
