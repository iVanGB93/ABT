from django.db import models
from django.db.models.functions import Now
from job.models import Job
from django.contrib.auth.models import User
from business.models import Business
import os


def upload_to_item_list(instance, filename):
    filename = os.path.basename(filename)
    return f'items/{instance.business.name}/{filename}'

class Item_List(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_item_list, default='itemDefault.jpg')
    date = models.DateTimeField(db_default=Now())
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, related_name='item_list', null=True, blank=True)


    def __str__(self):
        return self.name + ' - ' + str(self.amount)

def upload_to_item(instance, filename):
    filename = os.path.basename(filename)
    return f'items/{instance.list.name}/{filename}'

class Item(models.Model):
    list = models.ForeignKey(Item_List, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=upload_to_item, default='itemDefault.jpg')
    date = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.name


class TestModel(models.Model):
    image = models.ImageField(upload_to='test/', default='testDefault.jpg')
