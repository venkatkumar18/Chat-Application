from celery import shared_task, current_task
import csv
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime
from .models import Chat_table,Chat
from chat_server import settings
import os
from django.core.mail import send_mail
from django.utils import timezone

dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id='AKIA5BLR3GLCK7RJMJ7N',
                                   aws_secret_access_key='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',
                                   region_name='us-east-1')
table = dynamodb_resource.Table('message')


# from .views import URL
# @shared_task
# def adding_task(x,y):
#     return x+y
@shared_task
def fetch_and_upload(room):
    # global settings.FILE_URL
    ses_client = boto3.client('ses', region_name='us-east-1')
    s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id='AKIA5BLR3GLCK7RJMJ7N',
                             aws_secret_access_key='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')
    # ses_client = boto3.client('dynamodb',region_name="us-east-1")
    s3_resource = boto3.resource('s3', aws_access_key_id='AKIA5BLR3GLCK7RJMJ7N',
                                 aws_secret_access_key='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',
                                 region_name="us-east-1")
    dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id='AKIA5BLR3GLCK7RJMJ7N',
                                       aws_secret_access_key='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',
                                       region_name='us-east-1')

    table = dynamodb_resource.Table('message')
    print(table)

    fileNameFormat = 'chatRoom{}-{}'.format(room,datetime.now())
    csvFileName = '{}.csv'.format(fileNameFormat)

    response = table.scan(
        FilterExpression=Attr("chatRoom").eq(str(room)))

    if len(response['Items']) != 0:
        items = response['Items']
        keys = items[0].keys()
        response = response['Items']
        items = sorted(response,key=lambda x:x['id'])
        print('Current Working directory ' ,os.getcwd())
        # csvpath = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'CSV_FILES/' + csvFileName)
        csvpath = os.getcwd()+'/CSV_FILES/'+csvFileName
        for i in items:
            with open(csvpath, 'a') as f:
                dict_writer = csv.DictWriter(f, keys)
                # Here we check to see if its the first write.
                if f.tell() == 0:
                    dict_writer.writeheader()
                    dict_writer.writerow(i)
                else:
                    dict_writer.writerow(i)

        # args_access = {'ACL':'public-read'}
        s3Object = s3_resource.Object('assigchathistory', 'chat-history-backups/{}'.format(csvFileName))
        s3Response = s3Object.put(Body=open(csvpath, 'rb'))
        print(s3Response['ResponseMetadata']['HTTPStatusCode'])
        if s3Response['ResponseMetadata']['HTTPStatusCode'] == 200:
            settings.FILE_URL = s3_client.generate_presigned_url(ClientMethod='get_object',
                                                   Params={'Bucket': 'assigchathistory', 'Key': csvFileName})

            settings.FILE_URL = settings.FILE_URL[0: settings.FILE_URL.index('?')]
            settings.FILE_URL = settings.FILE_URL[:42] + 'chat-history-backups/' + settings.FILE_URL[42:]
            print('settings.FILE_URL inside celery - ', settings.FILE_URL)

            # ---------------------send - EMAil -------------------------
            users = Chat_table.objects.get(chatRoom=int(room))

            # timezone.localtime(users.date_time) + timedelta(days=2)

            mail_subject = "Chat History for room " + str(room)
            message = "I hereby attached the chat url for the messages in room "+str(room)+" receipient are " + users.hostEmail + ' and ' + users.participantEmail + '\n\nURL - ' + settings.FILE_URL+"\n\n\nNote - You can just click the link to download the chat history..."
            print('message - ',message)
            print('EMAIL host USER - ',settings.EMAIL_HOST_USER)
            # to_email = users.hostEmail
            send_mail(
                subject=mail_subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[users.hostEmail, users.participantEmail],
                # fail_silently=True,
            )
            print('SENT MAIL')
            users.status = "completed"
            users.chathistory = settings.FILE_URL
            users.completedDateTime = timezone.now()
            users.save()

        else:
            print('STATUS : FALSE')


    else:
        print('NO CHAT FOUND ON THIS ROOM')

@shared_task
def scheduler():
    ids = []
    for room in Chat_table.objects.raw("select id from api_chat_table where date(initiatedDatetime)=date(curdate()) and status='completed'"):
        response = table.scan(FilterExpression=Attr("chatRoom").eq(str(room.chatRoom)))
        response = response['Items']
        for j in response:
            ids.append(int(j['id']))

    for i in sorted(ids):
        table.delete_item(Key={'id': i})
    print('DELETED RECORDS IN DYNAMODB THROUGH SCHEDULER')
# @shared_task
# def celery_beat_30():
#     print('-----------------Inside celery beat executes every 30 seconds------------------')

# @shared_task
# def send_mail_func(room,url):
#     users = Chat_table().objects.get(chatRoom=int(room))
#
#     #timezone.localtime(users.date_time) + timedelta(days=2)
#     for user in users:
#         mail_subject = "Chat History for room "+str(room)
#         message = "I hereby attached the chat url for your messages"+\
#         "receipient are"+user.hostEmail+' '+user.participantEmail+' URL - '+settings.FILE_URL
#
#         # to_email = user.hostEmail
#         send_mail(
#             subject = mail_subject,
#             message=message,
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[user.hostEmail,user.participantEmail],
#             fail_silently=True,
#         )
#     return "Done Mail Sent"
#
#
