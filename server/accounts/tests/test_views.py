from django.test import TestCase
from unittest.mock import patch
import accounts.views

class SendLoginEmailViewTest(TestCase):
    '''Тест представления, которое отправляет
    сообщение для входа в систему'''

    def test_redirects_to_home_page(self):
        '''Тест: переадресуется на домашнюю страницу'''
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })
        self.assertRedirects(response, '/')
    
    # def test_sends_mail_to_address_from_post(self):
    #     '''Тест: отправляется сообщение на адрес из метода post'''
    #     self.send_mail_called = False

    #     def fake_send_mail(subject, body, from_email, to_list):
    #         '''Поддельная функция send_mail'''
    #         self.send_mail_called = True
    #         self.subject = subject
    #         self.body = body
    #         self.from_email = from_email
    #         self.to_list = to_list
        
    #     accounts.views.send_mail = fake_send_mail

    #     self.client.post('/accounts/send_login_email', data={
    #         'email': 'edith@example.com'
    #     })

    #     self.assertTrue(self.send_mail_called)
    #     self.assertEqual(self.subject, 'Your login link for Superlists')
    #     self.assertEqual(self.from_email, 'noreply@superlists')
    #     self.assertEqual(self.to_list, ['edith@example.com'])

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_adress_from_post(self, mock_send_mail):
        '''Тест: отправляется сообщение на адрес из метода post'''
        self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        })

        self.assertEqual(mock_send_mail.called, True)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Your login link for Superlists')
        self.assertEqual(from_email, 'noreply@superlists')
        self.assertEqual(to_list, ['edith@example.com'])


    def test_adds_success_message(self):
        '''Тест: добавляется сообщение об успехе'''
        response = self.client.post('/accounts/send_login_email', data={
            'email': 'edith@example.com'
        }, follow=True)

        message = list(response.context['messages'])[0]

        self.assertEqual(
            message.message,
            ("Check your email.")
        )
        self.assertEqual(message.tags, "success")
