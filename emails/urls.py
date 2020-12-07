from django.urls import path, include
from django.conf import settings

from .views import *
from . import views as web_views

app_name = 'emails'

urlpatterns = [
    path('mail/add', add_mail, name='add_mail'),
    path('mail/list', mail_list, name='mail_list'),

]