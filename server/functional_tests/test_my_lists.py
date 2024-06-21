from selenium.webdriver.common.by import By

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore

from .base import FunctionalTest
from .server_tools import create_session_on_server
from .management.commands.create_session import create_pre_authenticated_session
from server.settings import SERVER_EMAIL

User = get_user_model()

class MyListsTest(FunctionalTest):
    '''Тест приложения "Мои списки"'''
    
    def create_pre_authentication_session(self, email):
        '''Создать предварительно аутентифицированный сеанс'''
        if self.staging_server:
            session_key = create_session_on_server(self.c, self.staging_server, 'siteadmin', email)
        else:
            session_key = create_pre_authenticated_session(email)

        ## Установить cookie, которые нужны для первого посещения домена.
        ## страницы 404 загружаются быстрее всего!
        self.browser.get(self.live_server_url + "/404_no_such_url")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/'
        ))
    
    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        '''Тест: списки зарегистрированных пользователей сохраняются
        как "мои списки"'''
        email = 'edith@example.com' #SERVER_EMAIL
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Эдит является зарегистрированным пользователем
        self.create_pre_authentication_session(email)
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_in(email)

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        '''Тест: списки зарегистрированных пользователей сохраняются как "Мои списки"'''
        # Эдит является зарегистрированным пользователем
        self.create_pre_authentication_session('edith@example.com')

        # Эдит открывает домашнюю страницу и начинает новый список
        self.browser.get(self.live_server_url)
        self.add_list_item('Reticulate splines')
        self.add_list_item('Immanentize eschaton')
        first_list_url = self.browser.current_url

        # Она замечает ссылку на "Мои списки" в первый раз
        self.browser.find_element(By.LINK_TEXT, 'My lists').click()

        # Она видит, что ее список находится, и он назван на основе
        # первого элемента списка
        self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, 'Reticulate splines')
        )
        self.browser.find_element(By.LINK_TEXT, 'Reticulate splines').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # Она решает начать еще один список, чтобы только убедиться
        self.browser.get(self.live_server_url)
        self.add_list_item('Click cows')
        second_list_url = self.browser.current_url

        # Под заголовком "Мои списки" появляется ее новый список
        self.browser.find_element(By.LINK_TEXT, 'My lists').click()
        self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, 'Click cows')
        )
        self.browser.find_element(By.LINK_TEXT, 'Click cows').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # Она выходит из системы. Опция "Мои списки" исчезает
        self.browser.find_element(By.LINK_TEXT, 'Log out').click()
        self.wait_for(
            lambda: self.assertEqual(self.browser.find_elements(By.LINK_TEXT, 'My lists'), [])
        )