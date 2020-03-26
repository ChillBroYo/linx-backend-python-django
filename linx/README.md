Steps for deployment:
---------------------

(1) Setting up the DB
---------------------
In the directory with this readme run the following commands to setup the db:
- python3 manage.py makemigrations
- python3 manage.py migrate
- python3 manage.py migrate --run-syncdb

(2) After Setting up the db
---------------------------
Run the server on port 8080 with:
- python3 manage.py runserver 8080

(3) Fill with Dummy data
------------------------
Hit the end point and fill the db by going to those endpoints (drop them in your web browser):
- Add the user `sam`
  - http://localhost:8080/sign_up?uid=sam&password=123&info={"secret"="blah"}
  - you should get a `{"success": "true"}` back 
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}` 
- Add the user `kaya`
  - http://localhost:8080/sign_up?uid=kaya&password=123&info={"secret"="meh"}
  - you should get a `{"success": "true"}` back 
  - if you'd like to sanity check, hitting the endpoint again with the same user will send `{"success": "false", "errmsg": "Username Already Exists"}`
- Login user `sam` and `kaya`
  - http://localhost:8080/sign_in?uid=sam&password=123
  - you should get a `{"success": "true", "sam": "{*secret*=*blah*}"}` back
  - http://localhost:8080/sign_in?uid=kaya&password=123
  - you should get a `{"success": "true", "kaya": "{*secret*=*meh*}"}` back
- Have `kaya` send a message to `sam`
  - http://localhost:8080/add_message?uid=kaya&oid=sam&msg=Hello!
  - you should get a `{"success": "true"}` back 
- Look at the message between the 2:
  - http://localhost:8080/get_convo?uid=kaya&oid=sam
  - you should see the message sent above
- Have `sam` send a message to `kaya`
  - http://localhost:8080/add_message?uid=sam&oid=kaya&msg=Whoa!
  - you should get a `{"success": "true"}` back 
- Look at the conversation between the 2 again:
  - http://localhost:8080/get_convo?uid=kaya&oid=sam
  - you should see the new message sent above (note the UID and OID don't matter)
- Change user `sam`'s password and info
  - http://localhost:8080/update_profile?uid=sam&password=1234&info={"secret"="sicc"}
  - you should get a `{"success": "true"}` back
- Now see if you are locked out with the old password for sam and then use the new password and succeed
  - http://localhost:8080/sign_in?uid=sam&password=123
  - you should get `{"success": "false", "errmsg": "Invalid Password"}` back
  - http://localhost:8080/sign_in?uid=sam&password=1234
  - you should get `{"success": "true", "sam": "{*secret*=*sicc*}"}` back
- Provided this all works ... you should be all setup!

Endpoint Documentation
----------------------
Here are the endpoints and params:
- sign_up: used to sign up a user
  - params:
    - uid: username of new person to sign up
    - password: password of new person to sign up
    - info: user info in a mapping
  - returns:
    - jsonObject with a success flag of whether it succeeded or not

- sign_in: used to validate whether a user exists or not
  - params:
    - uid: username of person to sign in
    - password: password of person to sign in
  - returns:
    - jsonObject with a success flag of whether it succeeded or not

- add_message: used to add a message between 2 users
  - params:
    - uid: the user sending the message
    - oid: the user who is recieving the message
    - msg: the message sent
  - returns:
    - jsonObject with a success flag of whether it succeeded or not

- get_convo: used to see the whole message list between users
  - params:
    - uid: the first user
    - oid: the other user
  - returns:
    - jsonObject with all the messages between the 2 users

- update_profile: used to change the user profile info after sign up
  - params:
    - uid: the user to change
    - password: the password to change to
    - info: the user info the change to
  - returns:
    - jsonObject with a success flag of whether it succeeded or not
