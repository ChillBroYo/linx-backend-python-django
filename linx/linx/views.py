"""Webcall views dealing with all backend functionality"""
import uuid
import logging
import datetime
import boto3
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from linx.models import LUser, Messages, TokenAuth, Images, Reactions

# Get Logger
LOGGER = logging.getLogger('django')

# Unique Contraint on username and email field
# DEV ENDPOINT /sign_up, PROD ENDPOINT /sign-up
@csrf_exempt
def sign_up(request):
    """User signup through app based sign up strategy
        Only adds a new user and if sucessful creates a new key and returns the new uid and token
        POST Request Body Args:
            email (string): the user's email
            username (string): the user's username
            password (string): the user's password
            profile_picture (string): the link to the user's profile picture if desired
            security_level (string): the users security level, this should only be `user` for now
            info (json): any additonal information stored in JSON format
    """
    collected_values = {}

    # Only accept POST requests for this endpoint
    if request.method != 'POST':
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract Body Params
    email = request.POST['email']
    username = request.POST['username']
    password = request.POST['password']
    profile_picture = request.POST["profile_picture"]
    security_level = request.POST['security_level']
    info = request.POST['info']

    # Check if user with the same username already exists
    user = LUser.objects.filter(username=username)
    if user:
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Username Already Exists"
        return JsonResponse(collected_values, status=400)

    # Check if user with the same email exists
    user = LUser.objects.filter(email=email)
    if user:
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Email Already Exists"
        return JsonResponse(collected_values, status=400)

    # Create the user, with no images visited or friends
    new_user = LUser.create_luser(username=username, email=email, profile_picture=profile_picture,
                                  image_index=0, images_visited="[]", password=password,
                                  friends="[]", security_level=security_level, info=info)

    # Create new token for user in TokenAuth db
    collected_values["token"] = generate_new_token(new_user.user_id)

    # Store additional values for return message
    collected_values["success"] = "true"
    collected_values["uid"] = new_user.user_id

    LOGGER.info("Sign Up Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /sign_in, PROD ENDPOINT /sign-in
@csrf_exempt
def sign_in(request):
    """Sign in request that with either authentiate and acquire appropriate tokens or reject them
        GET Request Args:
            username: the user's username
            password: the user's password
    """
    collected_values = {}

    # Only accept GET requests for this endpoint
    if request.method != 'GET':
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    username = request.GET['username']
    password = request.GET['password']

    # Check if user exists
    user = LUser.objects.filter(username=username, password=password)
    if not user:
        collected_values["success"] = False
        collected_values["errmsg"] = "User doesn't exist"
        return JsonResponse(collected_values, status=400)

    # Get the token of the user and store it
    auth_user = TokenAuth.objects.filter(user_id=user[0].user_id)
    collected_values["token"] = auth_user[0].token

    # Collect remaining values
    collected_values["uid"] = user[0].user_id
    collected_values["email"] = user[0].email
    collected_values["username"] = user[0].username
    collected_values["password"] = user[0].password
    collected_values["info"] = str(user[0].info)
    collected_values["success"] = True

    LOGGER.info("Sign In Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /add_message, PROD ENDPOINT /add-message
@csrf_exempt
def add_message(request):
    """Add a message to the message table
        Args:
            uid: the user who sent the message's id
            oid: the user who is recieving the message's id
            token: a potentially valid token to use of the uid
            msg: the message to send
    """
    collected_values = {}

    # Only accept POST requests for this endpoint
    if request.method != 'POST':
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    uid = request.POST['uid']
    oid = request.POST['oid']
    token = request.POST['token']
    msg = request.POST['msg']

    # Check if token is valid, if not, return an error
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Create a message, do not specify the message id and store
    message = Messages(None, uid, oid, msg)
    message.save()
    collected_values["success"] = "true"

    LOGGER.info("Add Message Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /get_messages, PROD ENDPOINT /get-messages
@csrf_exempt
def get_conversation_list(request):
    """Gets a list of all the user profiles that a user has messaged
        Request Args:
        uid: the user's id
        token (string): a user's token for auth
        limit (int): the number of users to limit coming back
    """
    collected_values = {}

    # Only accept GET requests for this endpoint
    if request.method != 'GET':
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    uid = request.GET['uid']
    token = request.GET['token']
    limit = int(request.GET['limit']) # Force a limiter to see how many users to get

    # Check if the token is valid
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Maybe cache or find better way of getting most recent id's messaged
    # Do a walkthrough of all messages and count totals
    # Potential Improvement is to keep a mapping of all messages sent from users to users
    users = {}
    msg_sent = Messages.objects.filter(user_id=uid).order_by('-created_at')[:limit]
    msg_recieved = Messages.objects.filter(other_id=uid).order_by('-created_at')[:limit]
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
    
    # Collect return values
    collected_values["users"] = users
    collected_values["success"] = "true"

    LOGGER.info("Get Conversation List Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /get_conversation, PROD ENDPOINT /get-conversation
@csrf_exempt
def get_conversation(request):
    """Get the last 1000 message rows for a uid and another uid from a specified time
        Args:
            uid (string): a user's id
            oid (string): the other user's id
            token (string): a user's token for auth
            ts: timestamp to search behind
            limit: the limit of messages to search for
    """
    collected_values = {}

    # Only allow GET requests for this endpoint
    if request.method != 'GET':
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract and form params
    uid = request.GET['uid']
    oid = request.GET['oid']
    token = request.GET['token']
    ts_query = request.GET['ts']
    limit = int(request.GET['limit'])

    if ts_query == "":
        ts_query = timezone.now()

    # Check if token is valid
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = "false"
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Collect all messages sent by two users in question listed by created at time
    message_query_set = Messages.objects.filter(
        Q(user_id=uid, other_id=oid) |
        Q(other_id=uid, user_id=oid)).order_by('-created_at')[:limit]
    
    # Collect all messages from query
    test_list = []
    for message in message_query_set:
        test_list.append(message.get_map())

    # Collect return values
    collected_values["messages"] = test_list
    collected_values["success"] = True

    LOGGER.info("Get Conversation Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /update_profile, PROD ENDPOINT /update_profile
def update_profile(request):
    """Set the profile information for a user
        Args:
            uid: the user who sent the message's id
            username: the possibly new username for user
            password: the possibly new password for user
            token: a potentially valid token to use
            info: the user's possibly new info
    """
    objs = {}
    if request.method != 'POST':
        objs["success"] = "false"
        objs["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(objs)

    uid = request.GET['uid']
    email = request.GET['email']
    username = request.GET['username']
    password = request.GET['password']
    token = request.GET['token']
    info = request.GET['info']
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
            key: a key that prevents just anyone from hitting this endpoint, default 123
        NOTE: Allowing any user to get this info with a known secret
        (to be in the future made to each new app's app id)
    """
    objs = {}
    if request.method != 'GET':
        objs["success"] = "false"
        objs["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(objs)
    uid = request.GET['uid']
    key = request.GET['key']
    if key != "123":
        objs = {}
        objs["success"] = "false"
        objs["errmsg"] = "Invalid Token"
        return JsonResponse(objs)

    users = LUser.objects.filter(user_id=uid)
    user = users[0]
    user_info = user.get_map()

    LOGGER.info("Get Profile Result: %s", user)
    return JsonResponse(user_info)

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

def get_image(request):
    """Function to get the s3 image link
        Args:
            image_id (int): the id to look up
            image_type (string): the type of image to look up
    """
    objs = {}
    if request.method != 'GET':
        objs["success"] = "false"
        objs["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(objs)
    image_type = request.GET['image_type']
    image_id = request.GET['image_id']

    # General images are stored as g1, g2, g3 and so on, general
    # images also have an index that can be incremented through
    # Profile pictures are stored as p1, p2, p3 and so on
    prefix = ""
    if image_type == "general":
        prefix = "g"
    elif image_type == "profile":
        prefix = "p"
    elif image_type == "reference":
        prefix = "reference/"

    bucketname = 'linx-images' # bucket name
    filename = prefix + image_id # object key
    objs["image_url"] = "https://{}.s3-us-west-2.amazonaws.com/{}".format(bucketname, filename)

    LOGGER.info("Get Image Result: %s", objs)
    return JsonResponse(objs)

def save_image(request):
    """Function to save images to s3 and be recorded in the db
        Args:
            image (file): image to upload
            image_type (string): the type of image
            user_id (string): the user id who is trying to upload this image
    """
    objs = {}
    if request.method != 'POST':
        objs["success"] = "false"
        objs["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(objs)
    image = request.data['image']
    image_type = request.POST['image_type']
    user_id = request.POST['user_id']
    prefix = ""
    if image_type == "general":
        prefix = "g"
    elif image_type == "profile":
        prefix = "p"
    elif image_type == "reference":
        prefix = "reference/"

    s3 = boto3.resource('s3')
    bucket = s3.Bucket('linx-images')
    file_id = 0
    image_query_set = Images.objects.filter(
        Q(image_type=image_type)).order_by('-created_at')[:-1]

    file_index = -1
    if image_query_set:
        file_index = image_query_set[0].image_index
    else:
        objs["success"] = "false"
        objs["errmsg"] = "no images currently exist"
        return JsonResponse(objs)

    filename = "{}{}".format(prefix, file_index)

    objs = {}
    objs["success"] = "true"
    objs["image_type"] = image_type
    objs["image_url"] = "https://{}.s3-us-west-2.amazonaws.com/{}".format("linx-images", filename)
    image = Images(None, user_id, image_type, objs["image_url"])
    image.save()

    bucket.put_object(Key=filename, Body=image)

    return JsonResponse(objs)

def react_to_image(request):
    """Function to save images to s3 and be recorded in the db
        Args:
            uid (int): user's id
            image_id (int): the image that is being reacted to's id
            reaction_type (string): the reaction placed upon the image
    """
    objs = {}
    if request.method != 'POST':
        objs["success"] = "false"
        objs["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(objs)
    uid = request.GET['uid']
    image_id = request.GET['image_id']
    reaction_type = request.GET['reaction_type']

    # In this way, it is possible for a user to react the same way to the same
    # image with the same id
    reaction = Reactions(None, uid, image_id, reaction_type)
    reaction.save()
    objs["success"] = "true"
    return JsonResponse(objs)

def add_friend(request):
    pass
