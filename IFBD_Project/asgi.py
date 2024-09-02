from django.core.asgi import get_asgi_application
import os
from Messenger.routing import websocket_urlpatterns
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IFBD_Project.settings')


# def get_asgi_application():
#     from django.core.asgi import get_asgi_application
#     return get_asgi_application()

# django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
        {
                "http": get_asgi_application,
                "websocket":  AllowedHostsOriginValidator(
                    AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
                )
        }
)

