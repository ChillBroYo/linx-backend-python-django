"""Webcall views dealing with all backend functionality"""
import uuid
import json
import logging
import datetime
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from linx.models import LUser, Messages, TokenAuth


# Get Logger
LOGGER = logging.getLogger('django')

def sign_up(request):
    """User signup through app based sign up strategy
        Only adds a new user and if sucessful creates a new key and returns the new uid and token
        Request Args:
            email (string): the user's email
            username (string): the user's username
            password (string): the user's password
            info (json): any additonal information stored in JSON format
    """
    email = request.GET['email']
    username = request.GET['username']
    password = request.GET['password']
    security_level = request.GET['security_level']
    info = request.GET['info']
    user = LUser.objects.filter(username=username)
    if user:
        objs = {"success": "false", "errmsg": "Username Already Exists"}
        return JsonResponse(objs)

    objs = {}
    new_user = LUser.create_luser(username=username, email=email,
                                  password=password, security_level=security_level,
                                  info=info)

    objs["token"] = generate_new_token(new_user.user_id)
    objs["success"] = "true"
    objs["uid"] = new_user.user_id

    LOGGER.info("Sign Up Result: %s", json.dumps(str(objs)))
    return JsonResponse(objs)

def get_messages(request):
    """Gets a list of all the user profiles that a user has messaged
        Request Args:
        uid: the user's id
        token (string): a user's token for auth
    """
    uid = request.GET['uid']
    token = request.GET['token']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)
    objs["success"] = "true"
    users = {}
    # Maybe cache or find better way of getting most recent id's messaged
    msg_sent = Messages.objects.filter(user_id=uid).order_by('-created_at')[:1000]
    msg_recieved = Messages.objects.filter(other_id=uid).order_by('-created_at')[:1000]
    for msg in msg_sent:
        if users.get(msg.other_id) is None:
            users[msg.other_id] = 1
        else:
            users[msg.other_id] += 1
    for msg in msg_recieved:
        if users.get(msg.user_id) is None:
            users[msg.user_id] = 1
        else:
            users[msg.user_id] += 1
    objs["users"] = users

    LOGGER.info("Get Messages Result: %s", objs)
    return JsonResponse(objs)

def sign_in(request):
    """Sign in request that with either authentiate and generate appropriate tokens or reject them
        Request Args:
        username: the user's username
        password: the user's password
    """
    username = request.GET['username']
    password = request.GET['password']

    objs = {}
    objs["success"] = True
    user = LUser.objects.filter(username=username, password=password)
    if not user:
        objs = {}
        objs["success"] = False
        objs["errmsg"] = "User doesn't exist"
        return JsonResponse(objs)

    auth_user = TokenAuth.objects.filter(user_id=user[0].user_id)
    if not auth_user:
        objs["token"] = str(TokenAuth.create_token_for_user(user.user_id))
    else:
        objs["token"] = str(auth_user[0].token)

    objs["uid"] = user[0].user_id
    objs["email"] = user[0].email
    objs["username"] = user[0].username
    objs["password"] = user[0].password
    objs["info"] = str(user[0].info)
    LOGGER.info("Sign In Result: %s", objs)
    return JsonResponse(objs)

def add_message(request):
    """Add a message to the message table
        Args:
            uid: the user who sent the message's id
            oid: the user who is recieving the message's id
            token: a potentially valid token to use
            msg: the message to send
    """
    uid = request.GET['uid']
    oid = request.GET['oid']
    token = request.GET['token']
    msg = request.GET['msg']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)
    message = Messages(None, uid, oid, msg)
    message.save()
    objs["success"] = "true"

    LOGGER.info("Add Message Result: %s", objs)
    return JsonResponse(objs)

def update_profile(request):
    """Set the profile information for a user
        Args:
            uid: the user who sent the message's id
            username: the possibly new username for user
            password: the possibly new password for user
            token: a potentially valid token to use
            info: the user's possibly new info
    """
    uid = request.GET['uid']
    email = request.GET['email']
    username = request.GET['username']
    password = request.GET['password']
    token = request.GET['token']
    info = request.GET['info']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)

    LUser.objects.filter(user_id=uid).update(email=email,
                                             username=username, password=password, info=info)
    objs["success"] = "true"

    LOGGER.info("Update Profile Result: %s", objs)
    return JsonResponse(objs)

def get_profile(request):
    """Get the profile information for a user
        Args:
            uid: the user who sent the message's id
            token: a potentially valid token to use
    """
    uid = request.GET['uid']
    token = request.GET['token']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)
    users = LUser.objects.filter(user_id=uid)
    user = users[0]
    user_info = {}
    user_info["uid"] = user.user_id
    user_info["email"] = user.email
    user_info["username"] = user.username
    user_info["password"] = user.password
    user_info["info"] = str(user.info)

    LOGGER.info("Get Profile Result: %s", user)
    return JsonResponse(user_info)

def get_convo(request):
    """Get the last 1000 message rows for a uid and another uid from a specified time
        Args:
            uid (string): a user's id
            oid (string): the other user's id
            token (string): a user's token for auth
            ts: timestamp to search behind
    """
    objs = {}
    uid = request.GET['uid']
    oid = request.GET['oid']
    token = request.GET['token']
    ts_query = request.GET['ts']
    if ts_query == "":
        ts_query = timezone.now()
    is_valid, objs["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)
    objs["success"] = "true"
    message_query_set = Messages.objects.filter(
        Q(user_id=uid, other_id=oid) |
        Q(other_id=uid, user_id=oid)).order_by('-created_at')[:1000]
    print(message_query_set)
    test_list = []
    for message in message_query_set:
        print(message.get_map())
        test_list.append(message.get_map())
    objs["messages"] = test_list

    LOGGER.info("Get Convo Result: %s", objs)
    return JsonResponse(objs)

def check_auth(uid, token, ts_check):
    """Utility function used for checking if the token is valid for a user
        Args:
            uid (string): a user's id
            token (token string): a token value to check
            ts_check (timestamp): the ts of the time to check
    """
    if token is None:
        token_row = TokenAuth.objects.filter(user_id=uid).order_by("-created_at")[:1]
    else:
        token_row = TokenAuth.objects.filter(user_id=uid, token=token).order_by("-created_at")[:1]

    if not token_row:
        return False, None

    difference = ts_check - datetime.datetime.now()

    if difference.days > 90:
        return False, token_row[0].token
    return True, token_row[0].token

def generate_new_token(uid):
    """Function to generate authenticated users, auth tokens
        Args:
            uid (string): a user's id
    """
    random_token = uuid.uuid4()
    token = TokenAuth(user_id=uid, token=random_token)
    token.save()
    return random_token
    