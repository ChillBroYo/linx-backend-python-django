"""Webcall views dealing with all backend functionality"""
import uuid
import json
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import JsonResponse
from linx.models import User, Messages, TokenAuth

# Signup- Username doesn't have to be an email
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
    info = request.GET['info']
    user = authenticate(username=username, password=password)
    if user is not None:
        objs = {"success": "false", "errmsg": "Username Already Exists"}
        return JsonResponse(json.dumps(objs))

    objs = {}
    user = User.objects.create_user(username, email, password)
    user.info = info
    user.save()
    new_user = User.objects.filter(username=username, password=password)

    objs["token"] = generate_new_token(new_user.uid)
    objs["success"] = "true"
    objs["uid"] = new_user.uid

    return JsonResponse(json.dumps(objs))

def get_messages(request):
    """Gets a list of all the user profiles that a user has messaged
        Request Args:
        uid: the user's id
        token (string): a user's token for auth
    """
    uid = request.GET['uid']
    token = request.GET['token']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(json.dumps(objs))
    objs["success"] = "true"
    users = {}
    #: Maybe cache or find better way of getting most recent id's messaged
    message_sent = Messages.objects.filter(user_id=uid,
                                           ts__lte=datetime.now()).order_by('-ts')[:1000]
    message_recieved = Messages.objects.filter(other_id=uid,
                                               ts__lte=datetime.now()).order_by('-ts')[:1000]
    for msg in message_sent:
        if users.get(msg.user_id) is None:
            users[msg.user_id] = 1
        else:
            users[msg.user_id] += 1
    for msg in message_recieved:
        if users.get(msg.user_id) is None:
            users[msg.user_id] = 1
        else:
            users[msg.user_id] += 1
    objs["users"] = users

    return JsonResponse(json.dumps(objs))

def sign_in(request):
    """Sign in request that with either authentiate and generate appropriate tokens or reject them
        Request Args:
        username: the user's username
        password: the user's password
    """
    username = request.GET['username']
    password = request.GET['password']
    objs = {"success": "false"}
    messages = User.objects.filter(username=username, password=password)
    if messages is not None:
        is_valid_token, token = check_auth(messages[0].uid, None, None)
        if is_valid_token is False:
            objs["token"] = generate_new_token(messages[0].uid)
        else:
            objs["token"] = token
        objs["info"] = messages[0].info
        objs["success"] = "true"
    else:
        objs["errmsg"] = "Invalid username or password"

    return JsonResponse(json.dumps(objs))

def add_message(request):
    """Add a message to the message table
        Args:
            uid: the user who sent the message's id
            oid: the user who is recieving the message's id
            token: a potentially valid token to use
            msg: the message to send
            ts_query: timestamp on the message
    """
    uid = request.GET['uid']
    oid = request.GET['oid']
    token = request.GET['token']
    msg = request.GET['msg']
    ts_query = str(datetime.now())
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(json.dumps(objs))
    message = Messages(None, uid, oid, msg, ts_query)
    message.save()
    objs["success"] = "true"

    return JsonResponse(json.dumps(objs))

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
    username = request.GET['username']
    password = request.GET['password']
    token = request.GET['token']
    info = request.GET['info']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(json.dumps(objs))

    User.objects.filter(user_id=uid).update(username=username, password=password, info=info)
    objs["success"] = "true"

    return JsonResponse(json.dumps(objs))

def get_profile(request):
    """Get the profile information for a user
        Args:
            uid: the user who sent the message's id
            token: a potentially valid token to use
    """
    uid = request.GET['uid']
    token = request.GET['token']
    objs = {}
    is_valid, objs["token"] = check_auth(uid, token, datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(json.dumps(objs))
    user = User.objects.filter(user_id=uid)
    objs["username"] = user.username
    objs["password"] = user.password
    objs["info"] = user.info
    objs["success"] = "true"

    return JsonResponse(json.dumps(objs))

def get_convo(request):
    """Get the last 1000 message rows for a uid and another uid from a specified time
        Args:
            uid (string): a user's id
            oid (string): the other user's id
            token (string): a user's token for auth
            ts_query (time): time to query for
    """
    objs = {}
    uid = request.GET['uid']
    oid = request.GET['oid']
    token = request.GET['token']
    ts_query = request.GET['ts']
    is_valid, objs["token"] = check_auth(uid, token, datetime.now())
    if not is_valid:
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(json.dumps(objs))
    objs["success"] = "true"
    objs["messages"] = Messages.objects.filter(
        Q(uid=uid, oid=oid, ts__lte=ts_query) |
        Q(oid=uid, uid=oid, ts__lte=ts_query)).order_by('-ts')[:1000]
    return JsonResponse(json.dumps(objs))

def check_auth(uid, token, ts_check):
    """Utility function used for checking if the token is valid for a user
        Args:
            uid (string): a user's id
            token (token string): a token value to check
            ts_check (timestamp): the ts of the time to check
    """
    if token is None:
        token_row = TokenAuth.objects.filter(uid=uid).order_by("-created_at")[:1]
    else:
        token_row = TokenAuth.objects.filter(uid=uid, token=token).order_by("-created_at")[:1]

    if token_row is None:
        return False, None

    token_life = token_row[0].created_at+timedelta(hours=2)
    if ts_check < token_life:
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

def check_generate_token(uid, token):
    """Function to generate a new token if there isn't one
        Args:
            uid (string): a user's id
            token (string): a token match
    """
    exist, token = check_auth(uid, token, datetime.now())
    if not exist:
        new_token = generate_new_token(uid)
        print("User {} has expired token {} and is being given {}\n".format(uid, token, new_token))
        return new_token
    return token
    