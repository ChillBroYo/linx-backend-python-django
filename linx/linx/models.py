"""User, Messages and Tokens tables"""
from django.db import models

class User(models.Model):
    """User model for user information
        uid: auto generated user idenitification number
        username: user defined name that must also be unique
        password: user defined password encrypted by argon2
        info: any additonal information stored in JSON format
        created_at: the time the user was created
    """
    uid = models.AutoField(primary_key=True)
    username = models.CharField('username', max_length=50, primary_key=True)
    password = models.CharField('password', max_length=50)
    info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Messages(models.Model):
    """Messages model for all message data
        mid: auto generated message identification number
        user_id: user id of the user that sent the message
        other_id: user id of the user that recieved the message
        msg: the message sent
        created_at: the time the message was created
    """
    mid = models.AutoField(primary_key=True)
    user_id = models.CharField('user_id', max_length=50)
    other_id = models.CharField('other_id', max_length=50)
    msg = models.CharField('msg', max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

class TokenAuth(models.Model):
    """TokenAuth model for all token related data
        tid: auto generated token identification number
        user_id: the user id that properly authenticated
        token: a randomly generated string that is used to make message requests
        created_at: the time the token was created
    """
    tid = models.AutoField(primary_key=True)
    user_id = models.CharField('user_id', max_length=50)
    token = models.CharField('token', max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
