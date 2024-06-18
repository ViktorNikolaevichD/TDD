import sys

from django.core.mail import send_mail
from django.contrib import messages, auth
from django.urls import reverse
from django.shortcuts import redirect

from accounts.models import Token
from server.settings import SERVER_EMAIL

def send_login_email(request):
    '''Отправить сообщение для входа в систему'''
    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    message_body = f'Use this link to log in:\n\n{url}'
    send_mail(
        'Your login link for Superlists',
        message_body,
        SERVER_EMAIL,
        [email],
    )
    messages.success(
        request,
        ("Check your email.")
    )
    return redirect('/')

def login(request):
    '''Авторизовать пользователя'''
    print('login view', file=sys.stderr)
    uid = request.GET.get('token')
    user = auth.authenticate(request, uid=uid)
    print(user)
    if user:
        auth.login(request, user)
    return redirect('/')
