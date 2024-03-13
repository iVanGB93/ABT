from django.db import models
from django.db.models.functions import Now


def upload_to_item(instance, filename):
    return 'items/{filename}'.format(filename=filename)

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    price = models.IntegerField()
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_item, default='itemDefault.jpg')
    date = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.name
