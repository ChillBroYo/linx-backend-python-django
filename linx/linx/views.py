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

SUPER_SECURE_STRING = "123"

# Get Logger
LOGGER = logging.getLogger('django')

# Debug param to prevent bad s3 requests
DEV = True

ALAMEDA_COUNTY_ZIPS = ['94710', '94720', '95377', '95391', '94501', '94502', '94514', '94536', '94538', '94540', '94539', '94542', '94541', '94544',
                       '94546', '94545', '94552', '94551', '94555', '94560', '94566', '94568', '94577', '94579', '94578', '94580', '94586', '94588',
                       '94587', '94601', '94603', '94602', '94605', '94607', '94606', '94609', '94608', '94611', '94610', '94613', '94612', '94618',
                       '94619', '94621', '94660', '94661', '94701', '94703', '94702', '94705', '94704', '94707', '94706', '94709', '94708']
CONTRA_COASTA_COUNTY_ZIPS = ['94596', '94595', '94598', '94597', '94507', '94506', '94509', '94801', '94511', '94803', '94513', '94802', '94805',
                             '94804', '94807', '94517', '94516', '94806', '94519', '94518', '94521', '94520', '94523', '94525', '94526', '94505',
                             '94528', '94531', '94530', '94548', '94547', '94549', '94553', '94556', '94561', '94563', '94565', '94564', '94569',
                             '94572', '94583', '94582']
MARIN_COUNTY_ZIPS = ['94903', '94901', '94904', '94920', '94925', '94924', '94929', '94930', '94937', '94933', '94939', '94938', '94941', '94940',
                     '94947', '94946', '94949', '94948', '94950', '94957', '94956', '94963', '94960', '94965', '94964', '94970', '94971', '94973']
NAPA_COUNTY_ZIPS = ['94559', '94558', '94562', '94599', '94567', '94573', '94508', '94574', '94576']
SAN_FRANCISO_COUNTY_ZIPS = ['94102', '94104', '94103', '94105', '94108', '94107', '94110', '94109', '94112', '94111', '94115', '94114', '94117',
                            '94116', '94118', '94121', '94123', '94122', '94124', '94127', '94126', '94129', '94131', '94130', '94133', '94132',
                            '94134', '94139', '94143', '94151', '94159', '94158', '94188', '94177']
SAN_MATEO_COUNTY_ZIPS = ['94063', '94062', '94065', '94066', '94070', '94080', '94074', '94401', '94403', '94402', '94404', '94002', '94010',
                         '94005', '94014', '94015', '94018', '94020', '94019', '94021', '94025', '94027', '94030', '94038', '94037', '94044',
                         '94061', '94060']
SANTA_CLARA_COUNTY_ZIPS = ['94085', '94087', '94086', '94089', '94088', '95002', '95009', '95008', '95013', '95014', '95020', '95023', '95031',
                           '95030', '95033', '95032', '95035', '95037', '94301', '95042', '94303', '95044', '95050', '94305', '94304', '95046',
                           '95051', '94306', '95054', '95070', '95111', '95110', '95113', '95112', '95117', '95116', '95119', '95118', '95121',
                           '95120', '95123', '95122', '95125', '95124', '95127', '95126', '95129', '95128', '95131', '95130', '95133', '95132',
                           '95135', '95134', '95136', '95139', '95138', '95141', '95140', '95148', '94550', '95150', '94022', '94024', '95190',
                           '95192', '94028', '94040', '94041', '94043']
SOLANO_COUNTY_ZIPS = ['94590', '94589', '94592', '94591', '95688', '95618', '95687', '94534', '95620', '94533', '94535', '95694', '95625',
                      '94503', '94510', '94512', '94585']
SONOMA_COUNTY_ZIPS = ['95409', '95412', '95416', '95419', '95421', '95425', '95430', '95433', '95436', '95439', '95442', '95441', '95444',
                      '95446', '95445', '95448', '95450', '95452', '95462', '95465', '95472', '95471', '95476', '94515', '95486', '95492',
                      '95497', '94923', '94922', '94926', '94928', '94931', '94951', '94952', '94954', '94972', '95402', '95401', '95404',
                      '95403', '95405', '95407']
BAY_AREA_REGIONS = [ALAMEDA_COUNTY_ZIPS, CONTRA_COASTA_COUNTY_ZIPS, MARIN_COUNTY_ZIPS, NAPA_COUNTY_ZIPS, SAN_FRANCISO_COUNTY_ZIPS,
                    SAN_MATEO_COUNTY_ZIPS, SANTA_CLARA_COUNTY_ZIPS, SOLANO_COUNTY_ZIPS]
LA_COUNTY_ZIPS = ['90895', '91001', '91006', '91007', '91011', '91010', '91016', '91020', '91017', '93510', '91023', '91024', '91030', '91040',
                  '91043', '91042', '91101', '91103', '91105', '93534', '91104', '93532', '91107', '93536', '91106', '93535', '91108', '93539',
                  '93543', '93544', '91123', '93551', '93550', '91125', '93553', '93552', '91182', '93563', '91189', '91202', '91201', '93591',
                  '91204', '93599', '91203', '91206', '91205', '91208', '91207', '91210', '91214', '91302', '91301', '91304', '91303', '91306',
                  '91307', '91310', '91311', '91316', '91321', '91325', '91324', '91326', '91331', '91330', '91335', '91340', '91343', '91342',
                  '91345', '91344', '91350', '91346', '91352', '91351', '91354', '91356', '91355', '91357', '91361', '91364', '91367', '91365',
                  '91381', '91383', '91384', '91387', '91390', '91402', '91401', '91403', '91406', '91405', '91411', '91423', '91436', '91495',
                  '91501', '91502', '91505', '91504', '91506', '91602', '91601', '91604', '91606', '91605', '91608', '91607', '91614', '91706',
                  '91702', '91711', '91722', '91724', '91723', '91732', '91731', '91733', '91735', '91740', '91741', '91745', '91744', '91747',
                  '91746', '91748', '91750', '91755', '91754', '91759', '91765', '91767', '91766', '91768', '91770', '91773', '91772', '91776',
                  '91775', '91780', '91778', '91790', '91789', '91792', '91791', '91793', '91801', '91803', '91008', '92397', '90002', '90001',
                  '90004', '90003', '90006', '90005', '90008', '90007', '90010', '90012', '90011', '90014', '90013', '90016', '90015', '90018',
                  '90017', '90020', '90019', '90022', '90021', '90024', '90023', '90026', '90025', '90028', '90027', '90029', '90032', '90031',
                  '90034', '90033', '90036', '90035', '90038', '90037', '90040', '90039', '90042', '90041', '90044', '90043', '90046', '90045',
                  '90048', '90047', '90049', '90052', '90056', '90058', '90057', '90060', '90059', '90062', '90061', '90064', '90063', '90066',
                  '90065', '90068', '90067', '90069', '90071', '90074', '90077', '90084', '90089', '90095', '90094', '90096', '90099', '90201',
                  '90189', '90211', '90210', '90212', '90221', '90220', '90222', '90230', '90232', '90241', '90240', '90245', '90242', '90248',
                  '90247', '90250', '90249', '90254', '90260', '90255', '90262', '90264', '90263', '90266', '90265', '90270', '90274', '90272',
                  '90277', '90275', '90280', '90278', '90291', '90290', '90293', '90292', '90295', '90301', '90296', '90303', '90302', '90305',
                  '90304', '90402', '90401', '90404', '90403', '90406', '93243', '90405', '90501', '90503', '90502', '90505', '90504', '90508',
                  '90601', '90603', '90602', '90605', '90604', '90606', '90631', '90639', '90638', '90650', '90640', '90660', '90670', '90702',
                  '90701', '90704', '90703', '90706', '90710', '90713', '90712', '90715', '90717', '90716', '90731', '90723', '90733', '90732',
                  '90745', '90744', '90747', '90746', '90755', '90803', '90802', '90805', '90804', '90807', '90806', '90808', '90813', '90810',
                  '90815', '90814', '90840']
LA_REGIONS = [LA_COUNTY_ZIPS]

VALID_REGIONS = [BAY_AREA_REGIONS, LA_REGIONS]

def is_valid_linx_zip_helper(zip_code):
    for region in VALID_REGIONS:
        for county in region:
            if zip_code in county:
                return True
    return False

# Helper Endpoints
# DEV ENDPOINT /is_valid_linx_zip, PROD ENDPOINT /is-valid-linx-zip
@csrf_exempt
def is_valid_linx_zip(request):
    """Check if a zip code is in the valid zip code ranges
        Get Request Args:
            zip (string): the zip code to check
            key (string): password to block anyone from accessing
    """ 
    collected_values = {}

    if request.method != 'GET':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)
    email = request.GET['zip']
    key = request.GET['key']
    
    if key != SUPER_SECURE_STRING:
        collected_values["success"] = False
        collected_values["errmsg"] = "Unauthorized access"
        return JsonResponse(collected_values, status=400)

    if is_valid_linx_zip_helper(email):
        collected_values["success"] = True
        collected_values["is_valid"] = True
        return JsonResponse(collected_values, status=200)

    collected_values["success"] = True
    collected_values["is_valid"] = False

    LOGGER.info("Is valid linx zip result: %s", collected_values)
    return JsonResponse(collected_values, status=200)


# DEV ENDPOINT /common_images_between_users, PROD ENDPOINT /common-images-between-users
@csrf_exempt
def common_images_between_users(request):
    """Get a list of all the images are valid
        GET Request Args:
            user_id: the user id of the user requesting this
            token: the potentially token of the user_id specified
            oid: the other user's id to look up
    """
    collected_values = {}

    if request.method != 'GET':
        collected_values["success"] = False
        collected_values["errmsg"] = "Wrong HTTP verb"
        return JsonResponse(collected_values, status=400)

    collected_values["user_id"] = request.GET["user_id"]
    uid = collected_values["user_id"]
    collected_values["token"] = request.GET["token"]
    token = collected_values["token"]
    collected_values["oid"] = request.GET["oid"]
    oid = collected_values["oid"]

    # Check auth
    is_valid, collected_values["token"] = check_auth(uid, token, datetime.datetime.now())
    if not is_valid:
        collected_values["success"] = False
        collected_values["errmsg"] = "Invalid Token"
        return JsonResponse(collected_values, status=400)

    # Get all matching users and the image id from linx_reactions
    user_raw_query = "SELECT DISTINCT a.rid, a.iid FROM linx_reactions as a INNER JOIN linx_reactions as b ON a.iid = b.iid AND a.user_id == \'{}\' AND b.user_id = \'{}\' ORDER BY a.iid;".format(uid, oid)

    image_ids_to_list = Reactions.objects.raw(user_raw_query)

    image_ids = ""

    # Load rows to string
    for image_obj in image_ids_to_list:
        image_ids = image_ids + "\'" + str(image_obj.iid) + "\',"

    # Remove last comma
    image_ids = image_ids[:-1]

    image_links_query = "SELECT iid,link FROM linx_images WHERE iid IN ({});".format(image_ids)
    image_links_to_show = Images.objects.raw(image_links_query)
    list_image_ids = []
    for image_obj in image_links_to_show:
        list_image_ids.append(image_obj.link)

    collected_values["images_urls"] = list_image_ids
    collected_values["success"] = True

    LOGGER.info("Common images between users result: %s", collected_values)
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
                                  friends="[]", security_level=security_level, last_friend_added=datetime.datetime.now(),
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

# DEV ENDPOINT /get_conversation_list, PROD ENDPOINT /get-conversation-list
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
            tus: (time user seen) whether or not to mark the time that the user has seen these messages
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
    time_user_seen = request.GET.get('tus')
    limit = int(request.GET['limit'])

    if ts_query == "":
        ts_query = timezone.now()

    change_user_seen = False
    if time_user_seen == "true":
        change_user_seen = True

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
        if change_user_seen:
            message.time_user_seen = datetime.datetime.now()
            message.save()
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
    if key != SUPER_SECURE_STRING:
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
            key: a key that prevents just anyone from hitting this endpoint, default 123
        NOTE: Allowing any user to get this info with a known secret
        (to be in the future made to each new app's app id)
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
    collected_values["message"] = images[0].message
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
        bucket.put_object(Key=filename, Body=image.read())

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
