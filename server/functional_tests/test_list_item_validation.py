from .base import FunctionalTest
from unittest import skip
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class ItemValidationTest(FunctionalTest):
    '''Тест валидации элемента списка'''

    def get_error_element(self):
        '''Получить элемент с ошибкой'''
        return self.browser.find_element(By.CSS_SELECTOR, '.has-error')
    
    def test_cannot_add_empty_list_items(self):
        '''Тест: нельзя добавлять пустые элементы списка'''
        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)


        # Браузер перехватывает запрос и не загружает страницу со списком
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_text:invalid'))

        # # Домашняя страница обновляется, и появляется сообщение об ошибке,
        # # которое говорит, что элементы списка не должны быть пустыми
        # self.wait_for(lambda: self.assertEqual(
        #     self.browser.find_element(By.CSS_SELECTOR, '.has-error').text,
        #     'You can`t have an empty list item'
        # ))

        # Эдит начинает набирать текст нового элемента и ошибка исчезает
        self.get_item_input_box().send_keys('Buy milk')
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_text:valid'))

        # И она может отправить его успешно
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # # Она пробует снова, теперь с неким текстом для элемента, и теперь
        # # это срабатывает
        # self.get_item_input_box().send_keys('Buy milk')
        # self.get_item_input_box().send_keys(Keys.ENTER)
        # self.wait_for_row_in_list_table('1: Buy milk')

        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        self.get_item_input_box().send_keys(Keys.ENTER)

        # И снова браузен не подчинится
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_text:invalid'))

        # # Она получает аналогичное предупреждение на странице списка
        # self.wait_for(lambda: self.assertEqual(
        #     self.browser.find_element(By.CSS_SELECTOR, '.has-error').text,
        #     'You can`t have an empty list item'
        # ))

        # И она может его исправить, заполнив поле неким текстом
        self.get_item_input_box().send_keys('Make tea')
        self.wait_for(lambda: self.browser.find_element(By.CSS_SELECTOR, '#id_text:valid'))
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')
        self.wait_for_row_in_list_table('2: Make tea')

    def test_cannot_add_duplicate_item(self):
        '''Тест: нельзя добавлять повторяющиеся элементы'''
        # Эдит открывает домашнюю страницу и начинает новый список
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys('Buy wellies')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy wellies')

        # Она случайно пытается ввести повторяющийся элемент
        self.get_item_input_box().send_keys('Buy wellies')
        self.get_item_input_box().send_keys(Keys.ENTER)
        
        # Она видит полезное сообщение об ошибке
        self.wait_for(lambda: self.assertEqual(
            self.get_error_element().text,
            "You've already got this in your list"
        ))
    
    def test_error_messages_are_cleared_on_input(self):
        '''Тест: сообщения об ошибках очищаются при вводе'''
        # Эдит начинает список и вызывает ошибку валидации:
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys('Banter to thick')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Banter to thick')
        self.get_item_input_box().send_keys('Banter to thick')
        self.get_item_input_box().send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertTrue(
            self.get_error_element().is_displayed()
        ))

        # Она начинает набирать в поле ввода, чтобы очистить ошибку
        self.get_item_input_box().send_keys('a')

        # Она довольна от того, что сообщение об ошибке исчезает
        self.wait_for(lambda: self.assertFalse(
            self.get_error_element().is_displayed()
        ))
