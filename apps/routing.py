from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^search/(?P<key>\w+)/(?P<freq>\d+)/$', consumers.Consumer.as_asgi()),
]
