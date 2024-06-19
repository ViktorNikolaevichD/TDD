import getpass

from fabric import Connection, Config

def _get_manage_dot_py(host, user):
    '''Получить manage.py'''
    return f'/home/{user}/.cache/pypoetry/virtualenvs/tdd-* /home/{user}/sites/{host}/source/server/manage.py ' 

def reset_database(host, user):
    '''Обнулить базу данных'''
    manage_dot_py = _get_manage_dot_py(host, user)
    password = getpass.getpass("Enter your root password: ")
    config = Config(overrides={'sudo': {'password': password}})
    user = 'siteadmin'
    host = 'rememberlist.store'
    c = Connection(host='5.35.86.205', user='root', port=22, config=config, connect_kwargs={'password': password})
    c.run(f'{manage_dot_py} flush --noinput')

def create_session_on_server(host, email):
    '''Создать сеанс на сервере'''
    manage_dot_py = _get_manage_dot_py(host)
    password = getpass.getpass("Enter your root password: ")
    config = Config(overrides={'sudo': {'password': password}})
    user = 'siteadmin'
    host = 'rememberlist.store'
    c = Connection(host='5.35.86.205', user='root', port=22, config=config, connect_kwargs={'password': password})
    session_key = c.run(f'{manage_dot_py} create_session {email}')
    return session_key.strip()