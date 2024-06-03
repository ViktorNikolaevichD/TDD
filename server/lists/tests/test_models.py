from django.test import TestCase
from django.core.exceptions import ValidationError

from lists.models import Item, List

class ItemModelTest(TestCase):
    '''Тест модели элемента'''

    # def test_saving_and_retrieving_items(self):
    #     '''Тест сохранения и получения элементов списка'''
    #     list_ = List()
    #     list_.save()

    #     first_item = Item()
    #     first_item.text = 'The first (ever) list item'
    #     first_item.list = list_
    #     first_item.save()

    #     second_item = Item()
    #     second_item.text = 'Item the second'
    #     second_item.list = list_
    #     second_item.save()

    #     saved_list = List.objects.first()
    #     self.assertEqual(saved_list, list_)

    #     saved_items = Item.objects.all()
    #     self.assertEqual(saved_items.count(), 2)

    #     first_saved_item = saved_items[0]
    #     second_saved_item = saved_items[1]
    #     self.assertEqual(first_saved_item.text, 'The first (ever) list item')
    #     self.assertEqual(first_saved_item.list, list_)
    #     self.assertEqual(second_saved_item.text, 'Item the second')
    #     self.assertEqual(second_saved_item.list, list_)
    def test_default_text(self):
        '''Тест заданного по умолчанию текста'''
        item = Item()
        self.assertEqual(item.text, '')

    
    def test_cannot_save_empty_list_items(self):
        '''Тест: нельзя добавлять пустые элементы списка'''
        list_ = List.objects.create()
        item1 = Item(list=list_, text='')
        with self.assertRaises(ValidationError):
            item1.full_clean()
            item1.save()

    def test_duplicate_items_are_invalid(self):
        '''Тест: повторы элементов не допустимы'''
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='bla')
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='bla')
            item.full_clean()
    
    def test_CAN_save_item_to_different_lists(self):
        '''Тест: МОЖЕТ сохранять тот же элемент в разные списки'''
        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='bla')
        item = Item(list=list2, text='bla')
        item.full_clean() # Не должен поднять исключение

    def test_list_ordering(self):
        '''Тест: упорядочения списка'''
        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='i1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='3')
        self.assertEqual(
            list(Item.objects.all()),
            [item1, item2, item3]
        )
    
    def test_string_representation(self):
        '''Тест строкового представления'''
        item = Item(text='some text')
        self.assertEqual(str(item), 'some text')


class ListModelTest(TestCase):
    '''Тест модели элемента списка и элемента списка'''

    def test_item_is_related_to_list(self):
        '''Тест: связь элемента со списокм'''
        list_ = List.objects.create()
        item = Item()
        item.list = list_
        item.save()
        self.assertIn(item, list_.item_set.all())
    
    def test_get_absolute_url(self):
        '''Тест: получен абсолютный URL'''
        list_ = List.objects.create()
        self.assertEqual(list_.get_absolute_url(), f'/lists/{list_.pk}/')
