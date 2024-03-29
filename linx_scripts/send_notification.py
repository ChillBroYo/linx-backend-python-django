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

message = {
    "to": "ExponentPushToken[HPIB_SDbEknAAEpzLzMyPs]",
    "sound": "default",
    "title": "Original Title",
    "body": 'And here is the body',
    "data": { "info": 'goes here' },
  }
data = { "user_id": "1",
         "timestamp": "timestamp here",
         "type": "special"
         }
send_push_message("ExponentPushToken[HPIB_SDbEknAAEpzLzMyPs]", "Marco has sent you a messagee", data) 
