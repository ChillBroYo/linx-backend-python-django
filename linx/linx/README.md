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