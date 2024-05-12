from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://github.com/ViktorNikolaevichD/firstProject.git'

def deploy():
    '''Развернуть'''
    site_folder = f'/home/{env.user}/sites/{env.host}'
    source_forlder = site_folder + '/source/server'
    _create_directory_structure_if_necessery(site_folder)
    _get_latest_source(source_forlder)
    _update_settings(source_forlder, env.host)
    _updete_virtualenv(source_forlder)
    _update_static_files(source_folder)
    _update_database(source_forlder)


def _create_directory_structure_if_necessery(site_folder):
    '''Создать структуру каталога, если нужно'''
    for subfolder in ('static', 'source'):
        run(f'mkdir -p {site_folder}/{subfolder}')
    run(f'mkdir -p {site_folder}/source/database')

def _get_latest_source(source_folder):
    '''Получить самый свежий исходный код'''
    if exists(source_folder + '/.git'):
        run(f'cd {source_folder} && git fetch')
    else:
        run(f'git clone {REPO_URL} {source_folder}')
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run(f'cd {source_folder} && git reset --hard {current_commit}')