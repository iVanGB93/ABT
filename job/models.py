from django.db import models
from django.db.models.functions import Now
from client.models import Client
from django.contrib.auth.models import User

def upload_to_job(instance, filename):
    return 'jobs/{filename}'.format(filename=filename)

class Job(models.Model):
    status_options = {
        'new': 'NEW',
        'active': 'ACTIVE',
        'finished': 'FINISHED'
    }
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='provider', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=status_options, default='new')
    description = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    price = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_job, default='jobDefault.jpg')
    date = models.DateTimeField(db_default=Now())
    closed = models.BooleanField(default=False)

    def __str__(self):
            return f"{self.description} for {self.client}"
    
def upload_to_spent(instance, filename):
    return 'spents/{filename}'.format(filename=filename)

class Spent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job')
    description = models.CharField(max_length=150)
    amount = models.IntegerField()
    image = models.ImageField(upload_to=upload_to_spent, default='spentDefault.jpg')
    date = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.description
    
class Invoice(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='invoice')
    number = models.CharField(max_length=7, editable=False, unique=True)
    date = models.DateTimeField(db_default=Now())
    bill_to = models.ForeignKey(Client, on_delete=models.SET_NULL, related_name='client', null=True, blank=True)
    total = models.BigIntegerField()
    paid = models.BigIntegerField()
    due = models.BigIntegerField()
    closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:
            provider = str(self.job.provider.pk).zfill(3)[:3]
            last_invoice = Invoice.objects.filter(number__startswith=provider).order_by('-number').first()
            if last_invoice:
                last_number = last_invoice.number[-4:]
                new_number =  int(last_number) + 1
            else:
                new_number = 1
            self.number = provider + str(new_number).zfill(4)
        super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.number}"

class Charge(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='charges')
    description = models.CharField(max_length=150)
    amount = models.IntegerField()
