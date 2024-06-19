import time
import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

MAX_WAIT = 10


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


class FunctionalTest(StaticLiveServerTestCase):
    '''Функциональный тест'''

    def setUp(self):
        '''Установка'''
        self.browser = WebDriver()
        staging_server = os.environ.get('STAGING_SERVER')  # "rememberlist.store"  
        if staging_server:
            self.live_server_url = 'http://' + staging_server

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
