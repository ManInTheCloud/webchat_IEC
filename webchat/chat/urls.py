from django.conf.urls import url
from chat import views as chat_views

urlpatterns=[
    url(r'^$',chat_views.index),
    url(r'^homepage$',chat_views.index),
    url(r'(\d)$',chat_views.room),
]