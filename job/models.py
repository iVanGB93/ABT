from django.db import models
from django.db.models.functions import Now
from user.models import Profile

def upload_to_job(instance, filename):
    return 'jobs/{filename}'.format(filename=filename)

class Job(models.Model):
    status_options = {
        'new': 'NEW',
        'active': 'ACTIVE',
        'finished': 'FINISHED'
    }
    client = models.ForeignKey(Profile, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=status_options, default='new')
    description = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    price = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_job, default='jobDefault.jpg')
    date = models.DateTimeField(db_default=Now())
    closed = models.BooleanField(default=False)

def upload_to_spent(instance, filename):
    return 'spents/{filename}'.format(filename=filename)

def __str__(self):
        return self.description

class Spent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_spent, default='spentDefault.jpg')
    date = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.description