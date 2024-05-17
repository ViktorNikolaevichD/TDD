import getpass
from patchwork.files import exists, append
from fabric.exceptions import NothingToDo
from fabric import Connection, Config
from django.core.management.utils import get_random_secret_key

REPO_URL = 'https://github.com/ViktorNikolaevichD/TDD.git'


def deploy():
    '''Развернуть'''
    password = getpass.getpass("Enter your root password: ")
    config = Config(overrides={'sudo': {'password': password}})
    user = 'siteadmin'
    host = 'rememberlist.store'
    c = Connection(host='5.35.86.205', user='root', port=22, config=config, connect_kwargs={'password': password})
    site_folder = f'/home/{user}/sites/{host}'
    source_folder = site_folder + '/source'
    venv_folder = f'/home/{user}/.cache/pypoetry/virtualenvs/rememberlist-*'
    #_update_settings(c, source_folder, c.host)
    _create_directory_structure_if_necessery(c, site_folder)
    _get_latest_source(c, source_folder)
    _update_settings(c, source_folder, host)
    _update_virtualenv(c, source_folder, venv_folder)
    _update_static_files(c, source_folder, venv_folder)
    _update_database(c, source_folder, venv_folder)
    _change_owner(c, user, 'www-data', '/home/siteadmin')


def _create_directory_structure_if_necessery(c: Connection, site_folder):
    '''Создать структуру каталога, если нужно'''
    for subfolder in ('static', 'source'):
        c.run(f'mkdir -p {site_folder}/{subfolder}')


def _get_latest_source(c: Connection, source_folder):
    '''Получить самый свежий исходный код'''
    if exists(c, source_folder + '/.git'):
        c.run(f'cd {source_folder} && git fetch')
    else:
        c.run(f'git clone {REPO_URL} {source_folder}')
    c.run(f'mkdir -p {source_folder}/database')
    current_commit = c.local('git log -n 1 --format=%H', hide=True)
    c.run(f'cd {source_folder} && git reset --hard {current_commit.stdout}', hide=True)


def _update_settings(c: Connection, source_folder, site_name):
    '''Обновить настройки'''
    settings_path = source_folder + '/server/server/settings.py'

    c.run(f'sed -ri "s/DEBUG = True/DEBUG = False/g" {settings_path}', hide=True)
    c.run(f'sed -ri "s/ALLOWED_HOSTS = .+$/ALLOWED_HOSTS = [\'{site_name}\']/g" {settings_path}', hide=True)
    c.run(f'sed -ri "s/CSRF_TRUSTED_ORIGINS = .+$/CSRF_TRUSTED_ORIGINS = ' + \
          f'[\'https:\/\/*.{site_name}\', \'http:\/\/*.{site_name}\']/g" {settings_path}', hide=True)


    ## Здесь нужно будет в какой-то момент добавить виртуальное окружение для секретного ключа
    key = get_random_secret_key()

    c.run(f'sed -ri "s/SECRET_KEY = .+$/SECRET_KEY = \'{key}\'/g" {settings_path}', hide=True)
    

def _update_virtualenv(c: Connection, source_folder, venv_folder):
    '''Обновить виртуальную среду'''
    try:
        c.run(f'rm -r {venv_folder}')
    except NothingToDo:
        pass
    
    c.run(f'cd {source_folder} && poetry update')


def _update_static_files(c: Connection, source_folder, venv_folder):
    '''Обновить статические файлы'''
    with c.cd(f'{source_folder}/server'):
        c.run(f'{venv_folder}/bin/python manage.py collectstatic --noinput')


def _update_database(c: Connection, source_folder, venv_folder):
    '''Обновить базу данных'''
    with c.cd(f'{source_folder}/server'):
        c.run(f'{venv_folder}/bin/python manage.py migrate --noinput')


def _change_owner(c: Connection, user, group, owner_folder):
    '''Сменить владельца папки пользователя'''
    c.sudo(f'chown -R {user}:{group} {owner_folder}')


if __name__ == "__main__":
    deploy()
