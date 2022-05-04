from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # path('ws/<int:room>/', consumers.ChatConsumer.as_asgi()), # Using asgi
      path('ws/<int:room>/', consumers.ChatConsumer.as_asgi()),
]