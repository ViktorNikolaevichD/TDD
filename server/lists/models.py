from django.db import models
from django.urls import reverse


class List(models.Model):
    '''Список для элементов'''
    
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
