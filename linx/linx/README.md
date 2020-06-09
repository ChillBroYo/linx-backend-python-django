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
   - info: {"name":{"first":"Regina","last":"Willams"},"city":"San Francisco","state":"CA","distance"1.0,"birthday":"05/04/1984","ageRange":[23,29],"gender":"woman","sameGender":false,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://vignette.wikia.nocookie.net/veronicamars/images/1/16/Veronicas04.jpg/revision/latest/top-crop/width/720/height/900?cb=20190708150751"}
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Add the user `Tommy Brixton`
   - username: tswag
   - email: tfgh@aol.com
   - password: 123b
   - security_level: user
   - profile_picture: https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg
   - info: {"name":{"first":"Tommy","last":"Brixton"},"city":"San Francisco","state":"CA","distance"1.25,"birthday":"05/04/1997","ageRange":[23,29],"gender":"male","sameGender":false,"interests":["nature","food"],"sameInterests":true,"imgUrl":"https://static.billboard.com/files/media/bob-dylan-live-1969-rx-billboard-u-1548-1024x677.jpg"}
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Login user `bobhope`, `rwilliams`, and `tswag`
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

  ################################ --> below is unfinished
- Have `Regina Williams` send 1 message to `Tommy Brixton`
  - http://localhost:8080/add_message/?uid=2&oid=1&token=<YOUR-USER2-SESSION-TOKEN-HERE>&msg=hello2
  - you should get a `{"token": "<YOUR-USER2-SESSION-TOKEN-HERE>", "success": "true"}` back 
- Look at the conversation between the 2 again from the other's view:
  - http://localhost:8080/get_convo/?uid=2&oid=1&token=<YOUR-USER2-SESSION-TOKEN-HERE>&ts=
  - you should see the new message sent above (note the UID and OID don't matter only the token for making the request)
- See the users that `sam` has messaged:
  - http://localhost:8080/messages/?uid=1&token=<YOUR-USER1-SESSION-TOKEN-HERE>
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "users": {"2": 2}}`
  - this shows the id's of the users messaged and how many messages were sent by
- Change user `sam`'s password and info
  - http://localhost:8080/update_profile/?uid=1&email=sam@gmail.com&username=sam&password=1234&info=%7B%22secret%22=%22blah%22%7D&token=<YOUR-USER1-SESSION-TOKEN-HERE>
  - this should change the password to 1234
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true"}` back
- Now see if you are locked out with the old password for sam and then use the new password and succeed
  - http://localhost:8080/sign_in?uid=sam&password=123
  - you should get `{"success": false, "errmsg": "User doesn't exist"}` back
  - http://localhost:8080/sign_in?uid=sam&password=1234
  - you should get `{"success": true, "token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "uid": 1, "email": "sam@gmail.com", "username": "sam", "password": "1234", "info": "{\"secret\"=\"blah\"}"}` back
- Provided this all works ... you should be all setup!

Endpoint Documentation
----------------------
Here are the endpoints and params:
- sign_up: used to sign up a user
  - params:
    - username: username of new person to sign up
    - email: the email address of the new person
    - password: password of new person to sign up
    - info: user info in a mapping
  - returns:
    - jsonObject with a success flag of whether it succeeded or not and a user session token

- sign_in: used to validate whether a user exists or not
  - params:
    - username: username of person to sign in
    - password: password of person to sign in
  - returns:
    - jsonObject with a success flag of whether it succeeded or not, a user session token and the user's info

- add_message: used to add a message between 2 users
  - params:
    - uid: the user sending the message
    - oid: the user who is recieving the message
    - token: the UID's user session token
    - msg: the message sent
  - returns:
    - jsonObject with a success flag of whether it succeeded or not and a user session token

- get_convo: used to see the whole message list between users
  - params:
    - uid: the first user
    - oid: the other user
    - token: the UID's user session token
  - returns:
    - jsonObject with a success flag of whether it succeeded or not, a user session token and all the messages between the 2 users

- update_profile: used to change the user profile info after sign up
  - params:
    - uid: the user's id
    - username: username of new person to sign up
    - email: the email address of the new person
    - password: password of new person to sign up
    - token: the UID's user session token
    - info: user info in a mapping
  - returns:
    - jsonObject with a success flag of whether it succeeded or not and a user session token

- get_messages: used to get a user's messaged people and how many messages were sent to whom
  - params:
    - uid: the user's id
    - token: the UID's user session token
  - returns:
    - jsonObject with a success flag of whether it succeeded or not, a user session token and a list of all the user ids the user specified has been messaging from or to and how many messages there were (for ranking/priority)
