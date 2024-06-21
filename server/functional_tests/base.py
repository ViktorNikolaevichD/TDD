import time
import os
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from fabric import Connection, Config

from django.contrib.staticfiles.testing import StaticLiveServerTestCase


from .server_tools import reset_database

MAX_WAIT = 10


class FunctionalTest(StaticLiveServerTestCase):
    '''Функциональный тест'''

    def wait(fn):
        def modified_fn(*args, **kwargs):
            start_time = time.time()
            while True:
                try:
                    return fn(*args, **kwargs)
                except (AssertionError, WebDriverException) as e:
                    if time.time() - start_time > MAX_WAIT:
                        raise e
                    time.sleep(0.5)
        return modified_fn

    def setUp(self):
        '''Установка'''
        self.browser = WebDriver()
        self.staging_server = os.environ.get('STAGING_SERVER')  # "rememberlist.store"  
        if self.staging_server:
            self.live_server_url = 'http://' + self.staging_server
            password = "110884Vitiy*"
            config = Config(overrides={'sudo': {'password': password}})
            user = 'siteadmin'
            host = 'rememberlist.store'
            self.c = Connection(host='5.35.86.205', user='root', port=22, config=config, connect_kwargs={'password': password}) 
            reset_database(self.c, self.staging_server, 'siteadmin')

    def tearDown(self):
        '''Удаление'''
        self.browser.quit()
    
    @wait
    def wait_for(self, fn):
        '''Ожидать'''
        return fn()

    @wait
    def wait_for_row_in_list_table(self, row_text):
        '''Подтверждение наличия строки в таблице списка'''
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, 'id_list_table')
                rows = table.find_elements(By.TAG_NAME, 'tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def get_item_input_box(self):
        '''Получить поле ввода для элемента'''
        return self.browser.find_element(By.ID, 'id_text')
    
    @wait
    def wait_to_be_logged_in(self, email):
        '''Ожидать входа в систему'''
        self.wait_for(
            lambda: self.browser.find_element(By.LINK_TEXT, 'Log out')
        )
        navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
        self.assertIn(email, navbar.text)
    
    @wait
    def wait_to_be_logged_out(self, email):
        '''Ожидать выхода из системы'''
        self.wait_for(
            lambda: self.browser.find_element(By.NAME, 'email')
        )
        navbar = self.browser.find_element(By.CSS_SELECTOR, '.navbar')
        self.assertNotIn(email, navbar.text)

    def add_list_item(self, item_text):
        '''Добавить элемент списка'''
        num_rows = len(self.browser.find_elements(By.CSS_SELECTOR, '#id_list_table tr'))
        self.get_item_input_box().send_keys(item_text)
        self.get_item_input_box().send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f'{item_number}: {item_text}')
