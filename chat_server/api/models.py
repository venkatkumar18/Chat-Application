import pynamodb.expressions.condition
from django.db import models
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute,NumberAttribute,UTCDateTimeAttribute
from django.conf import settings
# pynamodb.expressions.condition.Comparison
class Chat_table(models.Model):
    hostEmail = models.EmailField()
    participantEmail=models.EmailField()
    chathistory=models.CharField(max_length=100)
    chatRoom =models.IntegerField()
    status =models.CharField(max_length=20)
    initiatedDateTime=models.DateTimeField()
    completedDateTime =models.DateTimeField()

class Chat(Model):
    class Meta:
        table_name = "message"
        region = "us-east-1"
        # host = 'http://localhost'
        # host = 'http://localhost:8000'
        aws_access_key_id = "AKIA5BLR3GLCK7RJMJ7N"
        aws_secret_access_key = "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"
    id = NumberAttribute(hash_key=True)
    chatRoom =UnicodeAttribute(null = True)
    createdDatetime = UTCDateTimeAttribute(null=True)
    fromEmail = UnicodeAttribute(null=True)
    toEmail = UnicodeAttribute(null=True)
    message = UnicodeAttribute(null=True)

if not Chat.exists():
    Chat.create_table(wait=True,read_capacity_units=1, write_capacity_units=1)