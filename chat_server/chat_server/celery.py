import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_server.settings')

celery_app = Celery('chat_server')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    'call-method-every-day': {
        'task': 'api.tasks.scheduler',
        'schedule': crontab(hour=23,minute= 59),
    },
}
celery_app.conf.timezone = 'UTC'