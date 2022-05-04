
from django.shortcuts import render, redirect,HttpResponseRedirect,reverse
from .models import Chat_table, Chat
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from . import get_id
from .tasks import fetch_and_upload,send_mail
from django.views.decorators.csrf import csrf_exempt
from boto3.dynamodb.conditions import Key, Attr
import boto3


from chat_server import settings
URL = ''
def home(request):
    print('INNNN HOME')
    return render(request, 'home.html')

def room(request,room):
    username = request.GET.get('username')
    room_detalis = Chat_table.objects.get(chatRoom=int(room))
    dynamodb_resource = boto3.resource('dynamodb', aws_access_key_id='AKIA5BLR3GLCK7RJMJ7N',
                                       aws_secret_access_key='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',
                                       region_name='us-east-1')

    table = dynamodb_resource.Table('message')
    response = table.scan(FilterExpression=Attr("chatRoom").eq(str(room)))
    response = response['Items']
    response = sorted(response,key=lambda x:x['id'])

    # messages = []
    # user = Chat()
    # n = get_id.get_just_id()-1
    # for i in range(n):
    #     for j in user.query(i+1,Chat.chatRoom==str(room)):
    #         messages.append(user.get(i+1))
    # print(messages)

    return render(request,'room.html', {
        'username':username,
        'room':room,
        'room_details':room_detalis,
        'messages':response
    })

def checkview(request):
    room = request.POST['room_name']
    username = request.POST['username']
    if Chat_table.objects.filter(chatRoom=int(room)).exists():
            obj = Chat_table.objects.get(chatRoom=int(room))
            if(obj.participantEmail!=''):
                raise Exception("Participant already joined the meeting")
            if(obj.status == 'completed'):
                raise Exception("Room already ended")
            obj.participantEmail = username
            obj.save()

    else:
        new_table = Chat_table.objects.create(hostEmail=username,
chathistory="",chatRoom=int(room),status="InProgress",initiatedDateTime=timezone.now()
                                              ,completedDateTime=timezone.now())
        #need to change the completed datetime at the end
    return redirect('/' + room + '/?username=' + username)

# @csrf_exempt
def trigger_celery(request,room):
    print('--------------------------------------------------------')
    print('Trigger_celery inside')
    # task = adding_task.delay(54,45)
    print(request.POST.get('username3'))
    print(request.POST.get('room_name3'))
    fetch_and_upload.delay(room)
    return redirect('home')
    # # print(task1)
    # print('---------------------------------------------------------')
    # # return redirect('home')
    # return True


def get_user_history(request):
    username = request.POST.get('username_to_search')
    query = "select id,chathistory from api_chat_table where hostEmail='{}' or participantEmail='{}'".format(username,username)
    print("query = ",query)
    history = []
    for j in Chat_table.objects.raw(query):
        history.append(j.chathistory)
    return render(request,'home.html',{
        'chat_history':history
    })