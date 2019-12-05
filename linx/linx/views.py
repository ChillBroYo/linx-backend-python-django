from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from linx.models import User, Messages
import requests
import json
import datetime

def get_convo(request):
    uid = "\"" + request.GET['uid'] + "\""
    oid = "\"" + request.GET['oid'] + "\""
    objs = []
    messages = Messages.objects.raw("SELECT 1 as id,* FROM messages AS m WHERE (m.user_id = {} and m.other_id = {}) or (m.other_id = {} and m.user_id = {}) ORDER BY m.ts;".format(uid, oid, uid, oid))
    for val in messages:
        objs.append([val.user_id, val.msg, val.ts])
    return HttpResponse(json.dumps(objs), content_type="application/json")

def sign_up(request):
    uid = "\"" + request.GET['uid'] + "\""
    password = "\"" + request.GET['password'] + "\""
    info = "\"" + request.GET['info'] + "\""
    objs = {}
    messages = Messages.objects.raw("SELECT 1 as id,* from user WHERE username = {};".format(uid))
    if len(messages) > 0:
        objs = {"success": "false", "errmsg": "Username Already Exists"}
        return HttpResponse(json.dumps(objs), content_type="application/json")
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO user(username, password, info) VALUES({}, {}, {});".format(uid, password, info))
    objs["success"] = "true"

    return HttpResponse(json.dumps(objs), content_type="application/json")

def sign_in(request):
    uid = "\"" + request.GET['uid'] + "\""
    password = request.GET['password']
    objs = {}
    messages = User.objects.raw("SELECT 1 as id,* from user WHERE username = {};".format(uid))
    for val in messages:
        if val.password != password:
            objs = {"success": "false", "errmsg": "Invalid Password"}
            return HttpResponse(json.dumps(objs), content_type="application/json")
        else:
            objs["success"] = "true"
            objs[val.username] = val.info
    return HttpResponse(json.dumps(objs), content_type="application/json")

def add_message(request):
    uid = "\"" + request.GET['uid'] + "\""
    oid = "\"" + request.GET['oid'] + "\""
    msg = "\"" + request.GET['msg'] + "\""
    ts = "\"" + str(datetime.datetime.now()) + "\""
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

