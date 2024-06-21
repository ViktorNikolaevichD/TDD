from django.db import models
from django.urls import reverse
from django.conf import settings


class List(models.Model):
    '''Список для элементов'''
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)

    @property
    def name(self):
        '''Имя'''
        return self.item_set.first().text

    def get_absolute_url(self):
        return reverse("view_list", args=[self.pk])
    

class Item(models.Model):
    '''Элемент списка'''
    text = models.TextField(default='')
    list = models.ForeignKey(List, default=None, on_delete=models.CASCADE)

    class Meta:
        ordering = ('id', )
        unique_together = ('list', 'text')
    
    def __str__(self):
        return self.text
