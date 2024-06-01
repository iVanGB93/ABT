from django.db import models
from django.db.models.functions import Now
from job.models import Job
from django.contrib.auth.models import User


def upload_to_item_list(instance, filename):
    return 'items/{filename}'.format(filename=filename)

class Item_List(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price = models.IntegerField()
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_item_list, default='itemDefault.jpg')
    date = models.DateTimeField(db_default=Now())
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='item_list', null=True, blank=True)


    def __str__(self):
        return self.name + ' - ' + str(self.amount)

def upload_to_item(instance, filename):
    return 'items/{filename}'.format(filename=filename)

class Item(models.Model):
    list = models.ForeignKey(Item_List, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_item, default='itemDefault.jpg')
    date = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.name
