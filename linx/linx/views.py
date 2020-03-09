"""Webcall views dealing with all backend functionality"""
import uuid
import json
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.db import connection
from django.http import HttpResponse, JsonResponse
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

def get_convo(request):
    """Grab the last 1000 messages from the db for a specific uid, token and time and return them
    in a tuple array of messages in order sent/recieved (msg, timestamp)
        Request Args:
        uid: the user's id
        oid: the other user's id
        ts: the timestamp to look for at that time or before
    """
    uid = request.GET['uid']
    oid = request.GET['oid'] + "\""
    objs = []
    messages = Messages.objects.raw("SELECT 1 as id,* FROM messages AS m WHERE (m.user_id = {} and m.other_id = {}) or (m.other_id = {} and m.user_id = {}) ORDER BY m.ts;".format(uid, oid, uid, oid))
    for val in messages:
        objs.append([val.user_id, val.msg, val.ts])
    return HttpResponse(json.dumps(objs), content_type="application/json")

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
    uid = "\"" + request.GET['uid'] + "\""
    oid = "\"" + request.GET['oid'] + "\""
    msg = "\"" + request.GET['msg'] + "\""
    ts = "\"" + str(datetime.now()) + "\""
    objs = {}
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO messages(user_id, other_id, msg, ts) VALUES({}, {}, {}, {});".format(uid, oid, msg, ts))
    objs["success"] = "true"

    return HttpResponse(json.dumps(objs), content_type="application/json")

def update_profile(request):
    uid = "\"" + request.GET['uid'] + "\""
    password = "\"" + request.GET['password'] + "\""
    info = "\"" + request.GET['info'] + "\""
    objs = {}
    messages = Messages.objects.raw("SELECT 1 as id,* from user WHERE username = {};".format(uid))
    if len(messages) == 0:
        objs = {"success": "false", "errmsg": "Username Does Not Exist"}
        return HttpResponse(json.dumps(objs), content_type="application/json")
    with connection.cursor() as cursor:
        cursor.execute("UPDATE user SET password = {}, info = {} WHERE username = {};".format(password, info, uid))
    objs["success"] = "true"

    return HttpResponse(json.dumps(objs), content_type="application/json")

def get_messages(request):
    uid = "\"" + request.GET['uid'] + "\""
    objs = []
    messages = Messages.objects.raw("SELECT 1 as id, user_id, other_id FROM messages WHERE user_id = {} or oid = {} ORDER BY ts;".format(uid, uid))
    for val in messages:
        if val.user_id == request.GET["uid"]:
            objs.append(val.other_id)
        else:
            objs.append(val.user_id)
    objs = list(set(objs))
    return HttpResponse(json.dumps(objs), content_type="application/json")

def check_auth(uid, token, ts_check):
    """Utility function used for checking if the token is valid for a user
        Args:
            uid (string): a user's id
            token (token string): a token value to check
            ts_check (timestamp): the ts of the time to check
    """
    if token is None:
        token_row = TokenAuth.objects.filter(uid=uid).order_by("-created_at")
    else:
        token_row = TokenAuth.objects.filter(uid=uid, token=token).order_by("-created_at")

    if token_row is None:
        return False, None

    token_life = token_row.created_at+timedelta(hours=2)
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
