import time
import re
import imaplib
import email
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from django.core import mail

from .base import FunctionalTest
from server import settings

#TEST_EMAIL = '10xl.pro@mail.ru'
SUBJECT = 'Your login link for Superlists'

class LoginTest(FunctionalTest):
    '''Тест регистрации в системе'''

    def wait_for_email(self, test_email, subject):
        '''Ожидать электронное сообщение'''
        if not self.staging_server:
            local_email = mail.outbox[0]
            self.assertIn(test_email, local_email.to)
            self.assertEqual(local_email.subject, subject)
            return local_email.body
        
        time.sleep(2)
        imap = imaplib.IMAP4_SSL(settings.IMAP_SERVER, settings.IMAP_PORT)
        imap.login(settings.USER_NAME, settings.EMAIL_PASSWORD)
        imap.select("INBOX/ToMyself")
        _, data = imap.search(None, "UNSEEN")

        num = data[0].split()[-1]
        _, data = imap.fetch(num, 'RFC822')
        msg = email.message_from_bytes(data[0][1])

        sender = msg['From']
        recipient = msg['To']
        subject = msg['Subject']
        body = ''
        for part in msg.walk():
            body += part.get_payload()

        imap.close()
        imap.logout()
        return body
        # return (sender, recipient, subject, body)

    def test_can_get_email_link_to_log_in(self):
        '''Тест: можно получить ссылку по почте для регистрации'''
        # Эдит заходит на офигительный сайт суперсписков и впервые
        # замечает раздел "войти" в навигационной панели
        # Он говорит ей ввести свой адрес электронной почты, что она и делает
        if self.staging_server:
            test_email = '10xl.pro@mail.ru'
        else:
            test_email = 'edith@example.com'

        self.browser.get(self.live_server_url)
        self.browser.find_element(By.NAME, 'email').send_keys(test_email)
        self.browser.find_element(By.NAME, 'email').send_keys(Keys.ENTER)
        # Появляется сообщение, которое говорит, что ей на почту
        # было выслано электронное письмо
        #print(mail.outbox)
        self.wait_for(lambda: self.assertIn(
            'Check your email',
            self.browser.find_element(By.TAG_NAME, 'body').text
        ))

        # Эдит проверяет свою почту и находит сообщение
        #print(self.get_sent_email())
        body = self.wait_for_email(test_email, SUBJECT)

        # Оно содержит ссылку на url-адрес
        self.assertIn('Use this link to log in', body)
        url_search = re.search(r'https*://.+/.+$',body)
        if not url_search:
            self.fail(f'Could not find url in email body:\n{body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Эдит нажимает на ссылку
        self.browser.get(url)

        # Она зарегистрирована в системе
        self.wait_to_be_logged_in(email=test_email)

        # Теперь она выходит из системы
        self.browser.find_element(By.LINK_TEXT, 'Log out').click()

        # Она вышла из системы
        self.wait_to_be_logged_out(email=test_email)
