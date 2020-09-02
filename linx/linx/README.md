Steps for deployment:
---------------------

(1) Setting up the DB
---------------------
In the directory with this readme run the following commands to setup the db:
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 manage.py migrate --run-syncdb

(2) After Setting up the db (for local deployment)
---------------------------
Run the server on port 8080 with:
- python3 manage.py runserver 8080

(3) Fill with Dummy data
------------------------
NOTE: Seeing as some of these requests are POST requests you will need to know how to curl a post request in the terminal or use
another tool like Postman https://www.postman.com/ , use x-www-formurlencoded body parms, this guide will use Postman
Hit the end point and fill the db by going to those endpoints (drop them in your web browser):
- Add the user `Bob Hope`
  - http://localhost:8080/sign_up/
   - username: bobhope
   - email: bobhope@gmail.com
   - password: 123a
   - security_level: user
   - profile_picture: https://www.google.com/url?sa=i%26url=https%3A%2F%2Faminoapps.com%2Fc%2Fcats%2Fpage%2Fitem%2Fcute-kitten-of-the-day%2FMQkU_0IgJXvxpz467rm426Yjw12bYP8%26psig=AOvVaw395gRO4RoYavVYkIy_CbVf%26ust=1590554453390000%26source=images%26cd=vfe%26ved=0CAIQjRxqFwoTCIC12Z7b0OkCFQAAAAAdAAAAABAJ
   - info: {"name":{"first":"Bob","last":"Hope"},"city":"San Francisco","state":"CA","distance":25,"birthday":"05/04/2001","ageRange":[23,29],"gender":"woman","sameGender":true,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://www.google.com/url?sa=i%26url=https%3A%2F%2Faminoapps.com%2Fc%2Fcats%2Fpage%2Fitem%2Fcute-kitten-of-the-day%2FMQkU_0IgJXvxpz467rm426Yjw12bYP8%26psig=AOvVaw395gRO4RoYavVYkIy_CbVf%26ust=1590554453390000%26source=images%26cd=vfe%26ved=0CAIQjRxqFwoTCIC12Z7b0OkCFQAAAAAdAAAAABAJ"}
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Add the user `Regina Williams`
   - username: rwilliams
   - email: rwillaims@yahoo.com
   - password: 123a
   - security_level: user
   - profile_picture: https://vignette.wikia.nocookie.net/veronicamars/images/1/16/Veronicas04.jpg/revision/latest/top-crop/width/720/height/900?cb=20190708150751
   - info: {"name":{"first":"Regina","last":"Willams"},"city":"San Francisco","state":"CA","distance":1.0,"birthday":"05/04/1984","ageRange":[23,29],"gender":"woman","sameGender":false,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://vignette.wikia.nocookie.net/veronicamars/images/1/16/Veronicas04.jpg/revision/latest/top-crop/width/720/height/900?cb=20190708150751"}
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Add the user `Tommy Brixton`
   - username: tswag
   - email: tfgh@aol.com
   - password: 123b
   - security_level: user
   - profile_picture: https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg
   - info: {"name":{"first":"Tommy","last":"Brixton"},"city":"San Francisco","state":"CA","distance":1.25,"birthday":"05/04/1997","ageRange":[23,29],"gender":"male","sameGender":false,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg"}
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Login users with username `bobhope`, `rwilliams`, and `tswag`
  - http://localhost:8080/sign_in/?username=bobhope&password=123a
  - you should get a response with all information back (including the password, this will be the only way of accessing a password)
  - http://localhost:8080/sign_in/?username=rwilliams&password=123a
  - you should get a response with all information back
  - http://localhost:8080/sign_in/?username=tswag&password=123b
  - you should get a response with all information back
- Have `Bob Hope` send 2 messages to `Regina Williams`
  - http://localhost:8080/add_message/
   - uid: 1
   - oid: 2
   - token: <YOUR-USER1-SESSION-TOKEN-HERE>
   - msg: Hello there
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true"}` back 
  - http://localhost:8080/add_message/
   - uid: 1
   - oid: 2
   - token: <YOUR-USER1-SESSION-TOKEN-HERE>
   - msg: How be you
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true"}` back
- Look at `Regina`'s conversation list
  - http://localhost:8080/get_conversation_list/?uid=2&token=<YOUR-USER2-SESSION-TOKEN-HERE>&limit=1000
  - You should see that there were 2 messages sent from user 1
- Look at the conversation between the `Bob` and `Regina` from `Regina`'s view:
  - http://localhost:8080/get_conversation/?uid=2&oid=1&token=<YOUR-USER1-SESSION-TOKEN-HERE>&ts=
  - you should see the 2 messages sent above
- Have `Regina Williams` send 1 message to `Tommy Brixton`
   - http://localhost:8080/add_message/
   - uid: 2
   - oid: 3
   - token: <YOUR-USER1-SESSION-TOKEN-HERE>
   - msg: Who's this chillbroyo Bob Hope?
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true"}` back
- Look at `Regina`'s conversation list
  - http://localhost:8080/get_conversation_list/?uid=2&token=<YOUR-USER2-SESSION-TOKEN-HERE>&limit=1000
  - You should see that there were 2 messages sent from user 1 AND 1 Message from 2 to 3
- Look at `Tommy Brixton`'s profile information
  - localhost:8080/get_profile/?uid=3&key=123
  - you should get the user's profile information
- Confirm `Tommy Brixton`'s current password login
  - localhost:8080/sign_in/?username=tswag&password=123b
  - you should get the user's info
- Change user `Tommy Brixton`'s password
  - http://localhost:8080/update_profile/
  - user_id:3
  - username:tswag
  - password:abc
  - email:tfgh@aol.com
  - profile_picture:https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg
  - image_index:0
  - images_visited:[]
  - friends:[]
  - security_level:user
    info:{"name":{"first":"Tommy","last":"Brixton"},"city":"San Francisco","state":"CA","distance":1.25,"birthday":"05/04/1997","ageRange":[23,29],"gender":"male","sameGender":false,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg"}
  - token:986c36f2-2937-4f38-81d4-5ef2eb4def66
  - this should change the password to 1234
- Confirm that `Tommy Brixton`'s password has been changed
  - localhost:8080/sign_in/?username=tswag&password=123b
  - you should get a message that the user does not exist
  - localhost:8080/sign_in/?username=tswag&password=abc
  - you should get the user's info
- Fake save a profile image to `Tommy Brixton`
  - localhost:8080/save_image/
  - image: <your image you upload>
  - token: <YOUR-USER3-SESSION-TOKEN-HERE>
  - image_type: profile
- See the new image uploaded and the new profile picture for `Tommy Brixton`
  - localhost:8080/get_image/?image_type=profile&image_index=0
  - you should see the image info that has just been uploaded
  - localhost:8080/get_profile/?uid=3&key=123
  - you should see that the profile picture link has been changed to the new url
- Fake save a general image from `Tommy Brixton`
  - localhost:8080/save_image/
  - image: <image you want to upload>
  - token: <YOUR-USER3-SESSION-TOKEN-HERE>
  - image_type: general
- Have `Bob Hope` react with a `smiley face` to `Tommy Brixton`'s photo
  - localhost:8080/react_to_image/
  - uid:1
  - token:545d92e4-2174-4ab1-8fa8-dc404321126f
  - image_id:1
  - reaction_type:smiley face


- IT IS KEY TO NOTE, save_image functionality is linked directly to the buckets, the DEV param blocks accidental pushes to the s3 db,
  turn it to False to make it push to s3

(4) You ain't got time to hit these endpoints and gimme that sql query right here
---------------------------------------------------------------------------------
- Here's insert statements to run in a brand new database that will fill with enough to run some queries on
  - INSERT INTO linx_luser(username,password,profile_picture,email,security_level,info,image_index,images_visited,friends,created_at,last_friend_added,time_user_seen,friend_not_to_add) 
VALUES(
    'tswag', '123', 'https://linx-images.s3-us-west-2.amazonaws.com/p0', 'tfgh@aol.com', 'user',
    '{"birthday":"04/24/1992","connectWith":{"ageRange":[23,29],"distance":25,"sameGender":false,"sameInterests":false},"expoPushToken":"","gender":"man","imgUrl":"","interests":[],"isOnboarded":false,"lastReaction":"2020-08-27T03:30:45","location":{"city":"San Jose","state":"CA","zip":"95121"},"name":{"first":"Tommy","last":"Brixton"}}',
    0,
    '[]',
    '[2]',
    '2020-08-27 03:31:47.212218',
    '2020-09-02 02:01:15.555931',
    '2020-09-02 02:01:15.555892',
    '[]'
),
(
    'rwilliams', '123', 'https://linx-images.s3-us-west-2.amazonaws.com/p0', 'rwilliams@gmail.com', 'user',
    '{"birthday":"04/24/1991","connectWith":{"ageRange":[24,29],"distance":25,"sameGender":false,"sameInterests":false},"expoPushToken":"","gender":"woman","imgUrl":"","interests":[],"isOnboarded":false,"lastReaction":"2020-08-27T03:30:45","location":{"city":"San Jose","state":"CA","zip":"95121"},"name":{"first":"Rebecca","last":"Williams"}}',
    0,
    '[]',
    '[1,3]',
    '2020-08-27 03:31:47.212218',
    '2020-09-02 02:01:15.555931',
    '2020-09-02 02:01:15.555892',
    '[]'
),
(
    'bobhope', '123', 'https://linx-images.s3-us-west-2.amazonaws.com/p0', 'bhope@aol.com', 'user',
    '{"birthday":"05/24/1992","connectWith":{"ageRange":[23,29],"distance":25,"sameGender":false,"sameInterests":false},"expoPushToken":"","gender":"man","imgUrl":"","interests":[],"isOnboarded":false,"lastReaction":"2020-08-27T03:30:45","location":{"city":"San Jose","state":"CA","zip":"95121"},"name":{"first":"Bob","last":"Hope"}}',
    0,
    '[]',
    '[2]',
    '2020-08-27 03:31:47.212218',
    '2020-09-02 02:01:15.555931',
    '2020-09-02 02:01:15.555892',
    '[]'
);
  - INSERT INTO linx_tokenauth(tid,user_id,token,created_at)
VALUES(
    1,1,
    '0afb8e0f-84ba-499c-aa60-b6dae52e2de2',
    '2020-06-12 09:09:53.214164'
),
(
    2,2,
    '43985ece-e49d-477f-b843-3a5501799ef7',
    '2020-06-13 21:05:21.745610'
),
(
    3,3,
    'cf5ee422-30f5-42c5-b0e8-2ac2592c765f',
    '2020-06-13 21:06:05.494443'
);
  - INSERT INTO linx_messages(user_id, other_id, msg, created_at, time_user_seen, users_notified)
VALUES(
    2,3,'hello therea','2020-08-27 03:32:52.628336','03:33:02',true
),
(
    2,1,'hello thereb','2020-08-27 03:32:52.628336','03:33:02',true
),
(
    1,2,'hello therec','2020-08-27 03:32:52.628336','03:33:02',true
);
