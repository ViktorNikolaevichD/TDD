import getpass
import sys

from fabric import Connection, Config

def _get_manage_dot_py(host, user):
    '''Получить manage.py'''
    return f'/home/{user}/.cache/pypoetry/virtualenvs/tdd-*/bin/python /home/{user}/sites/{host}/source/server/manage.py' 

def reset_database(c, host, user):
    '''Обнулить базу данных'''
    manage_dot_py = _get_manage_dot_py(host, user)
    
    c.run(f'{manage_dot_py} flush --noinput')

def create_session_on_server(c, host, user, email):
    '''Создать сеанс на сервере'''
    manage_dot_py = _get_manage_dot_py(host, user)
    session_key = c.run(f'{manage_dot_py} create_session {email}', hide=True)
    return session_key.stdout.strip()