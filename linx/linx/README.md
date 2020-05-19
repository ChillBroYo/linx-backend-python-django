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
- (if you want to have access to this ip outside of your current server, or for production change the IP)
  - python3 manage.py runserver 0.0.0.0:8080

(3) Fill with Dummy data
------------------------
Hit the end point and fill the db by going to those endpoints (drop them in your web browser):
- Add the user `sam`
  - http://localhost:8080/sign_up/?email=sam@gmail.com&username=sam&password=123&security_level=user&info=%7B%22secret%22=%22blah%22%7D
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true", "uid": 1}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Add the user `sam2`
  - http://localhost:8080/sign_up/?email=sam2@gmail.com&username=sam2&password=123&security_level=user&info=%7B%22secret%22=%22blah%22%7D
  - you should get a `{"token": "<YOUR-USER2-SESSION-TOKEN-HERE>", "success": "true", "uid": 2}` back
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}`
- Login user `sam` and `sam2`
  - http://localhost:8080/sign_in/?username=sam&password=123
  - you should get a `{"success": true, "token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "uid": 1, "email": "sam@gmail.com", "username": "sam", "password": "123", "info": "{\"secret\"=\"blah\"}"}` back
  - http://localhost:8080/sign_in/?username=sam2&password=123
  - you should get a `{"success": true, "token": "<YOUR-USER2-SESSION-TOKEN-HERE>", "uid": 2, "email": "sam2@gmail.com", "username": "sam2", "password": "123", "info": "{\"secret\"=\"blah\"}"}` back
- Have `sam` send a message to `sam2`
  - http://localhost:8080/add_message/?uid=1&oid=2&token=<YOUR-USER1-SESSION-TOKEN-HERE>&msg=there
  - you should get a `{"token": "<YOUR-USER1-SESSION-TOKEN-HERE>", "success": "true"}` back 
- Look at the message between the 2:
  - http://localhost:8080/get_convo/?uid=1&oid=2&token=<YOUR-USER1-SESSION-TOKEN-HERE>&ts=
  - you should see the message sent above
- Have `sam2` send a message to `sam`
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
