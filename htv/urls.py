"""htv URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import re_path
from django.contrib import admin

from django.views.decorators.cache import cache_page

from twitter_app.views import index, results, json_results


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', index),
    re_path(r'^search/(?P<key>\w+)/$', results, name="searching"),
    re_path(r'^search/(?P<key>\w+)/(?P<freq>\d+)/$', cache_page(0)(results), name="searching"),
    re_path(r'^json/(?P<key>\w+)/$', cache_page(0)(json_results), name="json_response"),
]
