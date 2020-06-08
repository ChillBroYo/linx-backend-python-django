"""User, Messages and Tokens tables
TBD IMPROVEMENTS: Create different table to "cache" a user's recent messages to people
"""
import uuid
import json
from django.db import models
from django.utils.timezone import now

class LUser(models.Model):
    """User model for user information
        uid: auto generated user idenitification number
        username: user defined name that must also be unique
        password: user defined password encrypted by argon2
        email: user email address
        profile_picture: the user's optionally uploaded profile picture link
        image_index: the user's current image index location
        images_visited: a list of integers referring to the id's of images the user has visited
        friends: a map of user_ids to the timestamp when the friendship was made
        security_level: the security level of the user
        info: any additonal information stored in JSON format
        created_at: the time the user was created
    """
    user_id = models.AutoField(primary_key=True)
    username = models.CharField('username', max_length=50, unique=True)
    password = models.CharField('password', max_length=50)
    profile_picture = models.TextField(blank=True)
    email = models.CharField('email', max_length=100)
    security_level = models.CharField('security_level', max_length=50)
    info = models.TextField(blank=True)
    image_index = models.IntegerField(auto_created=False)
    images_visited = models.TextField(blank=True)
    friends = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now, editable=False)

    def get_map(self):
        """Return the object as a map"""
        return_object = {}
        return_object["user_id"] = self.user_id
        return_object["username"] = self.username
        return_object["email"] = self.email
        return_object["profile_picture"] = self.profile_picture
        return_object["image_index"] = self.image_index
        return_object["images_visited"] = self.images_visited
        return_object["friends"] = self.friends
        return_object["security_level"] = self.security_level
        return_object["info"] = self.info
        return_object["created_at"] = self.created_at.__str__()
        return return_object

    def get_json(self):
        """Return the object as formmatted json"""
        return_object = {}
        return_object["user_id"] = self.user_id
        return_object["username"] = self.username
        return_object["email"] = self.email
        return_object["profile_picture"] = self.profile_picture
        return_object["image_index"] = self.image_index
        return_object["images_visited"] = self.images_visited
        return_object["friends"] = self.friends
        return_object["security_level"] = self.security_level
        return_object["info"] = self.info
        return_object["created_at"] = self.created_at.__str__()
        return json.dumps(return_object)

    def __str__(self):
        return '''UID: {}, Username: {}, Password: {}, Security Level: {},
         Info: {}, Created at: {}'''.format(
             self.user_id, self.username, self.password,
             self.security_level, self.info, self.created_at)

    @classmethod
    def create_luser(cls, username, password, email,
                     profile_picture, image_index, images_visited,
                     friends, security_level, info) -> object:
        """Creates a User object, saves it to the db and returns a copy of the object back
             username: user defined name that must also be unique
            password: user defined password encrypted by argon2
            email: user email address
            profile_picture: the user's optionally uploaded profile picture link
            image_index: the user's current image index location
            images_visited: a list of integers referring to the id's of images the user has visited
            friends: a map of user_ids to the timestamp when the friendship was made
            security_level: the security level of the user
            info: any additonal information stored in JSON format
        """
        new_user = LUser(username=username, password=password, email=email,
                         profile_picture=profile_picture, image_index=image_index,
                         images_visited=images_visited, friends=friends,
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

    def get_map(self):
        """Return the object as a map"""
        return_object = {}
        return_object["message_id"] = self.mid
        return_object["user_id"] = self.user_id
        return_object["other_id"] = self.other_id
        return_object["message"] = self.msg
        return_object["created_at"] = self.created_at.__str__()
        return return_object

    def get_json(self):
        """Return the object as formatted json"""
        return_object = {}
        return_object["message_id"] = self.mid
        return_object["user_id"] = self.user_id
        return_object["other_id"] = self.other_id
        return_object["message"] = self.msg
        return_object["created_at"] = self.created_at.__str__()
        return json.dumps(return_object)

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

class Images(models.Model):
    """Images model for all image info (no images stored on the db)
        iid: auto generated image identification number
        user_id: the user_id that uploaded this image
        link: the link to the s3 bucket storage location of the image
        image_index: the image's index to be displayed, only images to display will have indexes
        image_type: the type of image uploaded
        created_at: the time the image was uploaded
    """
    iid = models.AutoField(primary_key=True)
    user_id = models.CharField('user_id', max_length=50)
    image_index = models.IntegerField(null=True)
    image_type = models.CharField('image_type', max_length=50)
    link = models.TextField(blank=True)
    created_at = models.DateTimeField(default=now, editable=False)

class Reactions(models.Model):
    """Reactions model for all user reactions to specific images
    Considered going with a string addition strategy to allow for easy searching and
    computing but decided to go with basic solution for clarity and simplicity, may
    need a better performance solution for finding `matches` in the future
        rid: auto generated reaction idenitification number
        user_id: the user that reacted to the image
        iid: foreign key match to the Images table on image reacted to
        reaction_type: the type of reaction the user gave
        created_at: the time the reaction was marked
    """
    rid = models.AutoField(primary_key=True)
    user_id = models.CharField('user_id', max_length=50)
    iid = models.IntegerField(null=False)
    reaction_type = models.CharField('reaction_type', max_length=128)
    created_at = models.DateTimeField(default=now, editable=False)
