from unittest import skip

from django.test import TestCase
from django.utils.html import escape
from django.contrib.auth import get_user_model

from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR


User = get_user_model()


class HomePageTest(TestCase):
    '''Тест домашней страницы'''

    def test_home_home_template(self):
        '''Тест: использует домашний шаблон'''
        response = self.client.get('/')

        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_item_form(self):
        '''Тест: домашняя страница использует форму для элемента'''
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)

    # def test_home_page_return_correct_html(self):
    #     '''Тест: домашняя страница возвращает правильный html'''
    #     response = self.client.get('/')

    #     self.assertTemplateUsed(response, 'home.html')
        
    # def test_displays_all_list_items(self):
    #     '''Тест: отображаются все элементы списка'''
    #     Item.objects.create(text='itemy 1')
    #     Item.objects.create(text='itemy 2')

    #     response = self.client.get('/')

    #     self.assertIn('itemy 1', response.content.decode())
    #     self.assertIn('itemy 2', response.content.decode())


class ListViewTest(TestCase):
    '''Тест представления списка'''

# def test_validation_errors_end_up_on_lists_page(self):
#     '''Тест: ошибки валидации оканчиваются на странице списков'''
#     list_ = List.objects.create()
#     response = self.client.post(
#         f'/lists/{list_.id}/',
#         data={'text': ''}
#     )
#     self.assertEqual(response.status_code, 200)
#     self.assertTemplateUsed(response, 'list.html')
#     expected_error = escape('You can`t have an empty list item')
#     self.assertContains(response, expected_error)

    def post_invalid_input(self):
        '''Отправляет недопустимый ввода'''
        list_ = List.objects.create()
        return self.client.post(f'/lists/{list_.id}/', data={'text': ''})
    
    def test_for_invalid_input_nothing_saved_to_db(self):
        '''Тест: на недопустимый ввод: ничего не сохраняется в БД'''
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)
    
    def test_for_invalid_input_renders_list_template(self):
        '''Тест: на недопустимый ввод: отображается шаблон списка'''
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
    
    def test_for_invalid_input_passes_form_to_template(self):
        '''Тест: на недопустимый ввод: форма передается в шаблон'''
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        '''Тест: на недопустимый ввод: на странице показывается ошибка'''
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_uses_list_template(self):
        '''Тест: используется шаблон списка'''
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        '''Тест: отображаются элементы только для этого списка'''
        correct_list = List.objects.create()
        Item.objects.create(text='itemy 1', list=correct_list)
        Item.objects.create(text='itemy 2', list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text='other itemy 1', list=other_list)
        Item.objects.create(text='other itemy 2', list=other_list)
        
        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemy 1')
        self.assertContains(response, 'itemy 2')
        self.assertNotContains(response, 'other itemy 1')
        self.assertNotContains(response, 'other itemy 2')

        # list_ = List.objects.create()
        # Item.objects.create(text='itemy 1', list=list_)
        # Item.objects.create(text='itemy 2', list=list_)

        # response = self.client.get('/lists/unique-url/')

        # self.assertContains(response, 'itemy 1')
        # self.assertContains(response, 'itemy 2')

    def test_passes_correct_list_to_template(self):
        '''Тест: передается правильный шаблон списка'''
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_can_save_a_post_request_to_an_existing_list(self):
        '''Тест: можно сохранить post-запрос в существующий список'''
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_post_redirects_to_list_view(self):
        '''Тест: переадресуется в представление списка'''
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'A new item for an existing list'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')
    
    def test_display_item_form(self):
        '''Тест: отображения формы для элемента'''
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)
        self.assertContains(response, 'name="text"')
    
    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        '''Тест: ошибки валидации повторяющегося элемента
        оканчиваются на странице списков'''
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )    
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)

class NewListTest(TestCase):
    '''Тест нового списка'''

    def test_can_save_a_post_request(self):
        '''Тест: можно сохранить post-запрос'''
        self.client.post('/lists/new', data={'text': 'A new list item'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirect_after_post(self):
        '''Тест: переадресация после post-запроса'''
        response = self.client.post('/lists/new', data={'text': 'A new list item'})

        new_list = List.objects.first()
        # self.assertEqual(response.status_code, 302)
        # self.assertEqual(response['location'], '/lists/unique-url/')
        # Заменяет две предыдущие строки
        self.assertRedirects(response, f'/lists/{new_list.id}/')
        
        # self.assertIn('A new list item', responce.content.decode())
        # self.assertTemplateUsed(responce, 'home.html')
    
    # def test_validation_errors_are_sent_back_to_home_page_template(self):
    #     '''Тест: ошибки валидации отсылаются назад в шаблон домашней страницы'''
    #     response = self.client.post('/lists/new', data={'text': ''})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'home.html')
    #     expected_error = 'You can`t have an empty list item'
    #     self.assertContains(response, expected_error)
    
    def test_for_invalid_input_renders_home_template(self):
        '''Тест: на недопустимый ввод: отображае домашний шаблон'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_validation_errors_are_shown_on_home_page(self):
        '''Тест: ошибки валидации выводятся на домашней странице'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))
    
    def test_for_invalid_input_passes_form_to_template(self):
        '''Тест: на недопустимый ввод: форма передается в шаблон'''
        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_invalid_list_items_arent_saved(self):
        '''Тест: сохраняются недопустимые элементы списка'''
        self.client.post('/lists/new', data={'text': '1'})
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 1)

        list_ = List.objects.first()

        self.client.post(f'/lists/{list_.pk}/', data={'text': ''})
        self.assertEqual(List.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 1)

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        '''Тест: владелец сохраняется, если
        пользователь аутентифицирован'''
        user = User.objects.create(email='a@b.com')
        self.client.force_login(user)
        self.client.post('/lists/new', data={'text': 'new item'})
        list_ = List.objects.first()
        self.assertEqual(list_.owner, user)
    

class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        '''Тест: url-адрес для "моих списков" отображает соответсвующий
        им шаблон'''
        User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        '''Тест: передается правильный владелец в шаблон'''
        User.objects.create(email='wrong@owner.com')
        correct_user = User.objects.create(email='a@b.com')
        response = self.client.get('/lists/users/a@b.com/')
        self.assertEqual(response.context['owner'], correct_user)
