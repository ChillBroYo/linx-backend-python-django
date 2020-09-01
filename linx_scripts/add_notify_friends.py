import sqlite3
import requests
import datetime
import json
from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError

TIME_SINCE_LAST_REACTION_MINIMUM = 5
MINIMUM_IMAGES_IN_COMMON = 1

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

def is_valid_linx_zip(zip_code):
    for region in VALID_REGIONS:
        for county in region:
            if zip_code in county:
                return True
    return False

# Does not check if the zip_codes exist, run is_valid first
def in_same_city(first_zip, second_zip):
    for region in VALID_REGIONS:
        for county in region:
            if first_zip in county and second_zip in county:
                return True
    return False

# Basic arguments. You should extend this function with the push features you
# want to use, or simply pass in a `PushMessage` object.
def send_push_message(token, message, extra=None):
    try:
        response = PushClient().publish(
            PushMessage(to=token,
                        body=message,
                        data=extra))
        print("succeeded")
    except PushServerError as exc:
        print("issue1")
        print("{} ||| {} ||| {} ||| {}".format(message, extra, exc.errors, exc.response_data))
        # Encountered some likely formatting/validation error.
       # rollbar.report_exc_info(
       #     extra_data={
       #         'token': token,
       #         'message': message,
       #         'extra': extra,
       #         'errors': exc.errors,
       #         'response_data': exc.response_data,
       #     })
        raise
    except (ConnectionError, HTTPError) as exc:
        print("issue2")
        # Encountered some Connection or HTTP error - retry a few times in
        # case it is transient.
#        rollbar.report_exc_info(
#            extra_data={'token': token, 'message': message, 'extra': extra})
        raise self.retry(exc=exc)

    try:
        # We got a response back, but we don't know whether it's an error yet.
        # This call raises errors so we can handle them with normal exception
        # flows.
        response.validate_response()
        print("succeeded2")
    except DeviceNotRegisteredError:
        print("error3")
        # Mark the push token as inactive
        from notifications.models import PushToken
        PushToken.objects.filter(token=token).update(active=False)
    except PushResponseError as exc:
        # Encountered some other per-notification error.
        print("error")
#        rollbar.report_exc_info(
#            extra_data={
#                'token': token,
#                'message': message,
#                'extra': extra,
#                'push_response': exc.push_response._asdict(),
#            })
        raise self.retry(exc=exc)



sql_connect = sqlite3.connect('/home/ubuntu/linx-backend-python-django/linx/db.sqlite3')
cursor = sql_connect.cursor()

# Search for friends that are compatible
## Search for users that have reacted the same way to the same images
query = "SELECT DISTINCT a.iid as image_id, a.user_id as a_user, b.user_id as b_user FROM linx_reactions as a INNER JOIN linx_reactions as b ON a.iid = b.iid WHERE a.reaction_type = b.reaction_type AND a.user_id != b.user_id;"
reaction_results = cursor.execute(query).fetchall()

# Get all needed user info
query = "SELECT user_id, friends, info, last_friend_added, json_extract(info, '$.connectWith.sameGender') as same_gender,  json_extract(info, '$.gender') as gender FROM linx_luser ORDER BY user_id;"
friends_results = cursor.execute(query).fetchall()
sql_connect.close()

# Create a map of all a_users -> b_users -> how many times they have reacted the same
reaction_map = {}
for row in reaction_results:
    if reaction_map.get(row[1]) == None:
        reaction_map[row[1]] = {}
        reaction_map[row[1]][row[2]] = 1
    else:
        if reaction_map[row[1]].get(row[2]) == None:
            reaction_map[row[1]][row[2]] = 1
        else:
            reaction_map[row[1]][row[2]] += 1

# Create map of current user friends
user_to_friends_to_change = {}
for row in friends_results:
        # create dictionary of user_id to list
        user_to_friends_to_change[str(row[0])] = row[1].strip('][').split(',')

print("user to friends to change {}".format(user_to_friends_to_change))

# Create a map of users that are above the threshold for minimum "friendliness"
friends_to_match = []
for user in reaction_map:
    for matching_user in reaction_map[user]:
        if reaction_map[user][matching_user] >= MINIMUM_IMAGES_IN_COMMON:
            friend_combo = (user, matching_user)
            reverse_friend_combo = (matching_user, user)
            if len(friends_to_match) > 1:
#                if friend_combo in friends_to_match or reverse_friend_combo in friends_to_match:
                exists = False
                for combo in friends_to_match:
                    #print("about to compare {} to {}".format(friend_combo, friends_to_match))
                    if user in combo or matching_user in combo:
                        exists = True
                        break

                if exists == False:
                    failed_prior_check = False

                    # Ensure users want to match with the new friends gender
                    if friends_results[int(user) - 1][4] != 0 or friends_results[int(matching_user) - 1][4] != 0:
                        if friends_results[int(user) - 1][5] != friends_results[int(user) - 1][5]:
                            failed_prior_check = True

                    # Ensure users are within the correct zip codes available
                    loaded_info_1 = json.loads(friends_results[int(user) - 1][2])
                    loaded_info_2 = json.loads(friends_results[int(matching_user) - 1][2])
                    if (loaded_info_1["location"].get("zip") != None and loaded_info_2["location"].get("zip") != None
                        and is_valid_linx_zip(loaded_info_1["location"]["zip"])
                        and is_valid_linx_zip(loaded_info_2["location"]["zip"])
                        and in_same_city(loaded_info_1["location"]["zip"], loaded_info_2["location"]["zip"])
                        and failed_prior_check == False):
                        
                        if matching_user not in user_to_friends_to_change[user]:
                            friends_to_match.append(friend_combo)
                            friends_to_match.append(reverse_friend_combo)
            else:
                if matching_user not in user_to_friends_to_change[user]:
                    friends_to_match.append(friend_combo)
                    friends_to_match.append(reverse_friend_combo)

print("friends to match {}".format(friends_to_match))

# create new mapping of current users friends
new_user_friends = {}
for combo in friends_to_match:

    # create dictionary of user_id to list
    new_user_friends[str(combo[0])] = friends_results[int(combo[0]) - 1][1].strip('][').split(',')
    if new_user_friends[str(combo[0])][0] == "":
        new_user_friends[str(combo[0])].remove("")

    new_user_friends[str(combo[0])].append(combo[1])

print("new_user_friends {}".format(new_user_friends))

print("About to execute commands at {}".format(str(datetime.datetime.now())))
sql_connect = sqlite3.connect('/home/ubuntu/linx-backend-python-django/linx/db.sqlite3')
cursor = sql_connect.cursor()

ones_to_actually_notify = []
for user_id in new_user_friends:
    loaded_info = json.loads(friends_results[int(user_id) - 1][2])
    print(loaded_info["lastReaction"])
    last_reaction_time = datetime.datetime.strptime(loaded_info["lastReaction"].replace("T"," "), "%Y-%m-%d %H:%M:%S")
    last_friend_time = datetime.datetime.strptime(friends_results[int(user_id) - 1][3], "%Y-%m-%d %H:%M:%S.%f")
    last_reaction_elapsed = datetime.datetime.now() - last_reaction_time
    last_friend_elapsed = datetime.datetime.now() - last_friend_time
    if last_reaction_elapsed.days < TIME_SINCE_LAST_REACTION_MINIMUM and last_friend_elapsed.days > 1:
        ones_to_actually_notify.append(user_id)
        query = "UPDATE linx_luser SET friends=\'{}\' last_friend_added={} WHERE user_id = {}".format(new_user_friends[user_id], datetime.datetime.now(), user_id)
        print("About to run: {}".format(query))
        cursor.execute(query)
        sql_connect.commit()

sql_connect.close()


for user_id in ones_to_actually_notify:
    print("About to send notifications for user {}".format(user_id))
    loaded_info = json.loads(friends_results[int(user_id) - 1][2])
    expo_push_token = loaded_info["expoPushToken"]
    data = {"user_id": "{}".format(user_id),
         "timestamp": str(datetime.datetime.now()),
         "type": "friends"
         }
    send_push_message(expo_push_token, "You have a new friend! \uD83D\uDE00", data) 
