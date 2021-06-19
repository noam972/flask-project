<h1>Flask Project - RestAPI for messages</h1>

A REST API written in Flask, Python. <br>
DB - ClearDB(Mysql)<br>
Server - Heroku<br>

In order to use this api you need to sign up and then login to session. 

The API requests:
<br>
## POST: 
**Signup:** https://flask-project-api-msg.herokuapp.com/user/sign_up : JSON data with username and password.<br>
Example: {"username" : "Harel", "password" : "123456"}<br>
**Write message:** https://flask-project-api-msg.herokuapp.com/msg/write_msg
<br> 
Example: {"receiver" : "noa" , "message" : "Hi", "subject" : "how are you?", "creation_date" : "2021-06-18 19:00:57"}<br> 
##GET
**get all messages:** https://flask-project-api-msg.herokuapp.com/msg/get_all_messages - returns a list of messages and marks them as read. <br>
**get all unread messages:** https://flask-project-api-msg.herokuapp.com/msg/get_all_unread_messages - returns a list of unread messages and marks them as read. <br>
**read message:** https://flask-project-api-msg.herokuapp.com/msg/read_msg - returns the first unread message and mark as read. <br>
**delete message:** https://flask-project-api-msg.herokuapp.com/msg/delete_msg - delete the first message with the logged-in username as receiver or sender. <br>