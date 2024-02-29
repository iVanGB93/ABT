from django.db import models
from django.db.models.functions import Now

def upload_to_job(instance, filename):
    return 'jobs/{filename}'.format(filename=filename)

class Job(models.Model):
    status_options = {
        'new': 'NEW',
        'active': 'ACTIVE',
        'finished': 'FINISHED'
    }
    status = models.CharField(max_length=15, choices=status_options, default='new')
    client = models.CharField(max_length=30)
    description = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    price = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_job, default='jobs/jobDefault.jpg')
    date = models.DateTimeField(db_default=Now())
    closed = models.BooleanField(default=False)

def upload_to_spent(instance, filename):
    return 'spents/{filename}'.format(filename=filename)

class Spent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    description = models.CharField(max_length=150)
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_spent, default='spents/spentDefault.jpg')
    date = models.DateTimeField(db_default=Now())