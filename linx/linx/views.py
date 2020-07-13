"""Webcall views dealing with all backend functionality"""
import uuid
import logging
import datetime
import io
import boto3
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from linx.models import LUser, Messages, TokenAuth, Images, Reactions

# Get Logger
LOGGER = logging.getLogger('django')

# Debug param to prevent bad s3 requests
DEV = False

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
        collected_values["success"] = False
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
        collected_values["success"] = False
        collected_values["errmsg"] = "Username Already Exists"
        return JsonResponse(collected_values, status=400)

    # Check if user with the same email exists
    user = LUser.objects.filter(email=email)
    if user:
        collected_values["success"] = False
        collected_values["errmsg"] = "Email Already Exists"
        return JsonResponse(collected_values, status=400)

    # Create the user, with no images visited or friends
    new_user = LUser.create_luser(username=username, email=email, profile_picture=profile_picture,
                                  image_index=0, images_visited="[]", password=password,
                                  friends="[]", security_level=security_level, info=info)

    # Create new token for user in TokenAuth db
    collected_values["token"] = generate_new_token(new_user.user_id)

    # Store additional values for return message
    collected_values["success"] = True
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
        collected_values["success"] = False
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
        collected_values["success"] = False
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
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Create a message, do not specify the message id and store
    message = Messages(None, uid, oid, msg)
    message.save()
    collected_values["success"] = True

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
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    uid = request.GET['uid']
    token = request.GET['token']
    limit = int(request.GET['limit']) # Force a limiter to see how many users to get

    # Check if the token is valid
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = False
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
    collected_values["success"] = True

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
        collected_values["success"] = False
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
        collected_values["success"] = False
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

# DEV ENDPOINT /update_profile, PROD ENDPOINT /update-profile
@csrf_exempt
def update_profile(request):
    """Set the profile information for a user
        Args:
            uid: the user who sent the message's id
            username: the possibly new username for user
            password: the possibly new password for user
            email: the users possibly new email
            profile_picture: the users possibly new
            image_index: the user's image index they are currently at
            images_visited: the images that have been visited by the user by image id,
            friends: the friends that have been made by the user,
            security_level: the security level of the user, should only be user,
            token: a potentially valid token to use
            info: the user's possibly new info
    """
    collected_values = {}

    # Only allow POST requests with this endpoint
    if request.method != 'POST':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    uid = request.POST.get('user_id')
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    profile_picture = request.POST.get('profile_picture')
    image_index = request.POST.get('image_index')
    images_visited = request.POST.get('images_visited')
    friends = request.POST.get('friends')
    security_level = request.POST.get('security_level')
    token = request.POST.get('token')
    info = request.POST.get('info')

    # Check auth
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    user_obj = LUser.objects.filter(user_id=uid)[0]

    # Potentiall load object with valid values
    if username is not None: user_obj.username = username
    if password is not None: user_obj.password = password
    if email is not None: user_obj.email = email
    if profile_picture is not None: user_obj.profile_picture = profile_picture
    if image_index is not None: user_obj.image_index = image_index
    if images_visited is not None: user_obj.images_visited = images_visited
    if friends is not None: user_obj.friends = friends
    if security_level is not None: user_obj.security_level = security_level
    if info is not None: user_obj.info = info

    # Update user record
    user_obj.save()

    # Collect Return values
    collected_values["success"] = True

    LOGGER.info("Update Profile Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /get_profile, PROD ENDPOINT /get-profile
@csrf_exempt
def get_profile(request):
    """Get the profile information for a user
        Args:
            uid: the user who sent the message's id
            key: a key that prevents just anyone from hitting this endpoint, default 123
        NOTE: Allowing any user to get this info with a known secret
        (to be in the future made to each new app's app id)
    """
    collected_values = {}

    # Only allow GET requests on this endpoint
    if request.method != 'GET':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params
    uid = request.GET['uid']
    key = request.GET['key']

    # Hardcoded key for security
    if key != "123":
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Key"
        return JsonResponse(collected_values, status=400)

    # Grab the user's profile information
    users = LUser.objects.filter(user_id=uid)
    user = users[0]

    # Collect values
    collected_values["user_info"] = user.get_map()
    collected_values["success"] = True

    LOGGER.info("Get Profile Result: %s", user)
    return JsonResponse(collected_values, status=200)

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

# DEV ENDPOINT /get_image, PROD ENDPOINT /get-image
@csrf_exempt
def get_image(request):
    """Function to get the s3 image link
        Args:
            image_id (int): the id to look up
            image_type (string): the type of image to look up
    """
    collected_values = {}

    # Only allow GET requests for this endpoint
    if request.method != 'GET':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    image_type = request.GET['image_type']
    image_index = request.GET['image_index']

    # Check the DB for an image with the same image_type and id
    images = Images.objects.filter(image_type=image_type, image_index=image_index)
    if not images:
        collected_values["success"] = False
        collected_values["errmsg"] = "Image doesn't exist"
        return JsonResponse(collected_values, status=400)

    collected_values["image_index"] = images[0].image_index
    collected_values["image_id"] = images[0].iid
    collected_values["image_type"] = images[0].image_type
    collected_values["image_category"] = images[0].image_category
    collected_values["link"] = images[0].link
    collected_values["success"] = True

    LOGGER.info("Get Image Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /save_image, PROD ENDPOINT /save-image
@csrf_exempt
def save_image(request):
    """Function to save images to s3 and be recorded in the db
        Args:
            image (file): image to upload
            image_type (string): the type of image
            image_category (string): the category of the image
            user_id (string): the user id who is trying to upload this image
            token: a potentially valid token to use
    """
    collected_values = {}
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('linx-images')

    # Only allow POST requests on this endpoint
    if request.method != 'POST':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract params and build prefix
    image = request.FILES['image']
    image_type = request.POST['image_type']
    image_category = request.POST['image_category']
    user_id = request.POST['user_id']
    token = request.POST['token']
    prefix = ""
    ending_modifier = ""
    if image_type == "general":
        prefix = "g"
        ending_modifier = ".png"
    elif image_type == "profile":
        prefix = "p"
    elif image_type == "reference":
        prefix = "reference/"

    # Check auth
    is_valid, collected_values["token"] = check_auth(user_id, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Find the highest index image in that category and extract the index for the new image
    new_image_index = 0
    image_query_set = Images.objects.filter(
        Q(image_type=image_type)).order_by('-image_index')

    if image_query_set:
        new_image_index = image_query_set[0].image_index + 1

    # Load params into builders and save to the db and s3
    filename = "{}{}{}".format(prefix, new_image_index, ending_modifier)
    collected_values["image_type"] = image_type
    collected_values["image_url"] = "https://{}.s3-us-west-2.amazonaws.com/{}".format("linx-images", filename)
    image_to_save = Images(user_id=user_id, image_type=image_type,
                           link=collected_values["image_url"], image_category=image_category,
                           image_index=new_image_index)

    image_to_save.save()

    # DEV protection
    if not DEV:
        bucket.put_object(Key=filename, Body=image)

    # Profile picture modification on user
    if image_type == "profile":
        LUser.objects.filter(user_id=user_id).update(profile_picture=collected_values["image_url"])

    # Collect return values
    collected_values["success"] = True

    LOGGER.info("Add Image Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)

# DEV ENDPOINT /react_to_image, PROD ENDPOINT /react-to-image
@csrf_exempt
def react_to_image(request):
    """Function to save images to s3 and be recorded in the db
        Args:
            uid (int): user's id
            token: a potentially valid token to use
            image_id (int): the image that is being reacted to's id
            reaction_type (string): the reaction placed upon the image
    """
    collected_values = {}

    # Only allow POST requests for this endpoint
    if request.method != 'POST':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    # Extract Params
    uid = request.POST['uid']
    token = request.POST['token']
    image_id = request.POST['image_id']
    reaction_type = request.POST['reaction_type']

    # Check auth
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Make sure this image exists
    image_query_set = Images.objects.filter(
        Q(iid=image_id)).order_by('-image_index')

    if not image_query_set:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Image Id"
        return JsonResponse(collected_values, status=400)

    # Create a save reaction to image
    reaction = Reactions(user_id=uid, iid=image_id, reaction_type=reaction_type)
    reaction.save()

    # Collect values
    collected_values["success"] = True
    collected_values["reaction_type"] = reaction_type

    LOGGER.info("Add Reaction Result: %s", collected_values)
    return JsonResponse(collected_values, status=200)
