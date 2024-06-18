from django.contrib import admin
from django.urls import path, re_path

from accounts import views

urlpatterns = [
    re_path(r'^send_login_email$', views.send_login_email, name='send_login_email'),
    re_path(r'^login.*$', views.login, name='login'),
]
