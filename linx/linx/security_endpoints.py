import uuid, logging, pytz, io
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection

LOGGER = logging.getLogger('security')

# DEV Endpoint /delete_account, PROD ENDPOINT /delete-account
# NOTE This is a soft delete, the account needs to be manually erased
@csrf_exempt
def delete_account(request):
    """Soft deletes the users account, allowing another account to be created under the same username
        POST Request Args:
            user_id: the user id of the user that wants to delete their account
            token: the potentially correct token of the user_id specified
    """
    collected_values = {}
    
    if request.method != 'POST':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)
    
    uid = request.POST["user_id"]
    token = request.POST["token"]

    # Check auth
    is_valid, collected_values["token"] = check_auth(uid, token, timezone.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    change_query = "UPDATE linx_luser SET username = \'{}\' WHERE user_id = {}".format("DELETE ME", uid)
    with connection.cursor() as cursor:
        cursor.execute(change_query)

    collected_values["user_id"] = uid
    collected_values["token"] = token
    collected_values["executed_query"] = change_query

    LOGGER.info("Delete account request: %s", collected_values)
    return JsonResponse(collected_values, status=200)
    


# DEV ENDPOINT /remove_friend, PROD ENDPOINT /remove-friend
@csrf_exempt
def remove_friend(request):
    """Removes a friend from the list and adds them to the block list for each user
        If one user requests a block, these people can never connect again and are disconnected
        POST Request Args:
            user_id: the user id of the user requesting this
            oid: the user id of other user to block/remove
            token: the potentially correct token of the user_id specified
    """
    collected_values = {}

    if request.method != 'POST':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)
    
    uid = request.POST["user_id"]
    oid = request.POST["oid"]
    token = request.POST["token"]

    # Check auth
    is_valid, collected_values["token"] = check_auth(uid, token, timezone.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    user_raw_query = "SELECT friends, friend_not_to_add from linx_luser WHERE user_id = {}".format(uid)
    other_raw_query = "SELECT friends, friend_not_to_add from linx_luser WHERE user_id = {}".format(oid)
    with connection.cursor() as cursor:
        cursor.execute(user_raw_query)
        values = cursor.fetchall()
        user_friends = values[0][0]
        if user_friends == None:
                user_friends = ""
        user_blocked = values[0][1]
        if user_blocked == None:
                user_blocked = ""

        cursor.execute(other_raw_query)
        values = cursor.fetchall()
        other_friends = values[0][0]
        if other_friends == None:
                other_friends = ""
        other_blocked = values[0][1]
        if other_blocked == None:
                other_blocked = ""

        friendsr = user_friends.replace("[", "").replace("]", "")
        split_user_friends = friendsr.split(",")
        split_user_friends.remove(oid)
        new_user_friends = "[" + ",".join(split_user_friends) + "]"
    
        block_listr = user_blocked.replace("[", "").replace("]", "")
        block_list = block_listr.split(",")
        if block_list is []:
            block_list = [oid]
        else:
            block_list.append(oid)
        new_user_block = "[" + ",".join(block_list) + "]"

        ofriendsr = other_friends.replace("[", "").replace("]", "")
        other_friends = ofriendsr.split(",") 
        other_friends.remove(uid)
        new_other_friends = "[" + ",".join(other_friends) + "]"

        block_listr2 = other_blocked.replace("[", "").replace("]", "")
        block_list2 = block_listr2.split(",")
        if block_list2 is []:
            block_list2 = [uid]
        else:
            block_list2.append(uid)
        new_other_block = "[" + ",".join(block_list2) + "]"
    
        user_raw_query2 = "UPDATE linx_luser SET friends = \'{}\', friend_not_to_add = \'{}\' WHERE user_id = {}".format(new_user_friends, new_user_block, uid)
        other_raw_query2 = "UPDATE linx_luser SET friends = \'{}\', friend_not_to_add = \'{}\' WHERE user_id = {}".format(new_other_friends, new_other_block, oid)

        cursor.execute(user_raw_query2)
        cursor.execute(other_raw_query2)

        collected_values["uid"] = uid
        collected_values["oid"] = oid
        collected_values["token"] = token
        collected_values["raw_query_1"] = user_raw_query2
        collected_values["raw_query_2"] = other_raw_query2

    LOGGER.info("Block user request: %v", collected_values)
    return JsonResponse(collected_values, status=200)
    
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
                                  friends="[]", security_level=security_level, last_friend_added=timezone.now(),
                                  info=info)

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
    collected_values["friends"] = user[0].friends
    collected_values["success"] = True

    LOGGER.info("Sign In Result: %s", collected_values)
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

    difference = ts_check - timezone.now()

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
