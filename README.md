Creating Chat server using Django

Packages Used - 
  Django         -> version (3.1.13)   -> pip install Django
  channels       -> version (3.0.4)    -> pip install channels
  channels-redis -> veriosn(3.3.1)     -> pip install channels-redis
  daphne         -> version (3.0.2)    -> pip install daphne
  redis-server   -> version (6.0.9)    -> pip install redis-server
  asgi           ->version(1.4.3)      -> pip install asgi_redis
  mysqlclient    -> version (1.4.6)    -> pip install mysqlclient
  boto3          -> version(1.21.46)   -> pip install boto3
  pynamodb       -> version(4.3.3)     -> pip install pynamodb
  celery         -> version(5.1.2)     -> pip install celery

Installed App -> api  , added 'api.apps.ApiConfig' to INSTALLED_APPS,
                         channels , added channels to INSTALLED_APPS

Models:
   Created two models for this project
  
  Chat_table:
    *Used Mariadb for creating this table 
    *Used chatApplication as database 
    *Created 7 fields - hostEmail , participantEmail,chathistory,chatRoom,status,initiatedDateTime,completedDateTime and id(primary key)
    *initially setting the initiatedatetime and comlpetedDatetime to current time after the completion of the chat the completedDatetime is changed to that time
    *The First person who enter the room will be hostEmail , the second person to enter the same rom will be participantEmail.
    *Initially the chatHistory will be empty at the end it is modified , status is set to 'inprogress' after the end it will be changed to 'completed'
  Chat:
    *Used Dynamodb for creating this table
    *table_name = 'message'
    *region = 'us-east-1'
    *created 5 field - id(hash_key),fromEmail,toEmail,chatRoom,createdDatetime,message
    *getting the id from a file names id.txt (because setting it to static value overwrites the record once the server stoped and started again so only i created a file and get the id everytime by reading the value ) initially it is set to 1 after insertion it will increased by 1.
    *getting the createdDatetime from Chat_table.createdDatetime
    *getting the fromEmail and toEmail from Chat_table.fromEmail and toEmail by checking some condition to determine who is the sender and who is the receiver
    
Templates:
    home.html
      This is the home page of the application 
      it contains room_name textfield and username_textfield
      it contains search_user_history input_field to get the chat History of that user.
      
    Room.html
      It contains send button (To send the messages),say bye button(to send a default message that the user is going to leave the room),end chat(to end the chat).
 
 
 Web Socket :
    Used django-channels 
    Added ASGI_APPLICATION = 'chat_server.asgi.application' in settings
    Then registered the chatsocket in chat_server.asgi.py
    Then added the chatsocket URL in routing.py , and the request from the url is handled by functions in consumers.py
    In consumers.py created connect,disconnect,recieve and save_messages methods.
    
    In room.html ,when the user types the messages in inupt field and click send message then inside the script tag the chatsocket will be created to the url mentioned in routing.py. Then chatsocket.onmessage() and on.open() methods are created inside the script.
    if the send message button is clicked then the chatsocket will send the username,message and room which will be received in consumers.py and the message will be appended to the container in room.html and the message input field will be set to empty string.
    If the say bye button is clicked then a default message will be send thorugh the socket. The chatsocket will send the default message , username as admin and room number as 1000.
    In the save_message function wrtten in consumers.py is where we store the messages to dynamodb. There will be a condition to check if it is a normal message or the default messag send by admin at room number 1000.
    
Celery:
    I had used redis as message broker for celery
    All the celery configuration is written inside settings.py
    Then created the celery_app inside the chat_server.celery.py file.
    Wrote the celery methods inside api.tasks
    Once the End chat button is clicked the celery task fetch_and_upload will be triggered , it will get the room name as a parameter. The function will fetch all the records in the dynamodb belonging to the chatroom. Then it will convert the response['Items'] into a csv file. The csv file will be stored inside CSV_FILES locally. Then the csv file will be uploaded to Amazon S3. Then we will get the object_url and will send the object_url to hostEmail and participantEmail of that chatRoom through Email. The email is sent thorugh "smtp.gamil.com" service.All the email configurations are written inside settings.py .In the email the object_url is sent so the users can click the link and download the chat history. Atlast the object_url and completedDatetime is updated in Chat_table for that chatRoom. for fetching and uploading record i had used boto3 library.
    
Celery_ Beat:
    I had added the celery_beat configurations inside chat_server.celery.py file . I had configured in a way that it will call the scheduler method which is inside tasks at 11.59 pm everyday.
    The Scheduler will find the chatRoom which has the currentdate and status as completed in Chat_table(), Then it will delete all the entries in dynamodb which has the chatRoom matching from the Chat_table().
    
Steps for running the project
initiating redis  - redis-server
initiating celery - celery -A chat_server worker --loglevel=info
initiating celery beat - celery -A chat_server beat -l INFO


    
    
