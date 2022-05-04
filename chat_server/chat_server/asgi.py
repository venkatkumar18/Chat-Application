import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.http import AsgiHandler
# from chat_server.api import routing
import api.routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    )
})






# import os
#
# from django.core.asgi import get_asgi_application
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_server.settings')
#
# application = get_asgi_application()
#


# import os
#
# import django
# from channels.http import AsgiHandler
# from channels.routing import ProtocolTypeRouter
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_server.settings')
# django.setup()
#
# application = ProtocolTypeRouter({
#   "http": AsgiHandler(),
#   ## IMPORTANT::Just HTTP for now. (We can add other protocols later.)
# })



