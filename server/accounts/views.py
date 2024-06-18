from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect

def send_login_email(request):
    '''Отправить сообщение для входа в систему'''
    email = request.POST['email']
    send_mail(
        'Your login link for Superlists',
        'Use this link to log in',
        'noreply@superlists',
        [email],
    )
    messages.success(
        request,
        ("Check your email.")
    )
    return redirect('/')
