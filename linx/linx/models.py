"""User, Messages and Tokens tables
TBD IMPROVEMENTS: Create different table to "cache" a user's recent messages to people
"""
import uuid
from django.db import models
from django.utils.timezone import now

class LUser(models.Model):
    """User model for user information
        uid: auto generated user idenitification number
        username: user defined name that must also be unique
        password: user defined password encrypted by argon2
        security_level: the security level of the user
        info: any additonal information stored in JSON format
        created_at: the time the user was created
    """
    uid = models.AutoField(primary_key=True)
    username = models.CharField('username', max_length=50, unique=True)
    password = models.CharField('password', max_length=50)
    email = models.CharField('email', max_length=100)
    security_level = models.CharField('security_level', max_length=50)
    info = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return '''UID: {}, Username: {}, Password: {}, Security Level: {},
         Info: {}, Created at: {}'''.format(
             self.uid, self.username, self.password,
             self.security_level, self.info, self.created_at)

    @classmethod
    def create_luser(cls, username, password, email, security_level, info) -> object:
        """Creates a User object, saves it to the db and returns a copy of the object back
            username: user defined name that must also be unique
            password: user defined password encrypted by argon2
            security_level: the security level of the user
            info: any additonal information stored in JSON format
        """
        new_user = LUser(username=username,
                         password=password, email=email,
                         security_level=security_level, info=info)
        new_user.save()
        return new_user

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
    created_at = models.DateTimeField(default=now, editable=False)

    def __str__(self):
        return '''MID: {}, UID: {}, OID: {}, msg: {}, created_at: {}'''.format(
            self.mid, self.user_id, self.other_id, self.msg, self.created_at)

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
    created_at = models.DateTimeField(default=now, editable=False)

    @classmethod
    def create_token_for_user(cls, uid):
        """Create a token pairing with a user
            uid: the user id of the person to create a token with
        """
        token_obj = TokenAuth(user_id=uid, token=uuid.uuid4())
        token_obj.save()
        return token_obj
