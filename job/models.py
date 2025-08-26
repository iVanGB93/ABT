from django.db import models
from django.db.models.functions import Now
from client.models import Client
from django.contrib.auth.models import User
from business.models import Business, BusinessPaymentMethod
import os

def upload_to_job(instance, filename):
    filename = os.path.basename(filename)
    return f'jobs/{instance.business.name}/{instance.client.name}/{filename}'

class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),           # Awaiting client approval/start
        ('confirmed', 'Confirmed'),       # Client approved, ready to start
        ('in_progress', 'In Progress'),   # Currently being worked on
        ('on_hold', 'On Hold'),          # Temporarily paused
        ('review', 'Under Review'),       # Completed, awaiting client review
        ('completed', 'Completed'),       # Finished and approved
        ('cancelled', 'Cancelled'),       # Job was cancelled
        ('invoiced', 'Invoiced'),        # Invoice has been sent
        ('paid', 'Paid'),                # Payment received
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='jobs')
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='jobs', null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='jobs')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    description = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    address2 = models.CharField(max_length=50, default='no extra address saved')
    price = models.FloatField()
    image = models.ImageField(upload_to=upload_to_job, default='jobDefault.jpg')
    created_at = models.DateTimeField(db_default=Now())
    updated_at = models.DateTimeField(db_default=Now())
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    closed = models.BooleanField(default=False)
    payment_method_used = models.ForeignKey(
        BusinessPaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paid_jobs'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('partial', 'Partial'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
        ],
        default='pending'
    )

    def __str__(self):
            return f"{self.description} for {self.client}"
    
    
def upload_to_spent(instance, filename):
    filename = os.path.basename(filename)
    return f'spents/{instance.job.business.name}/{instance.job.client.name}/{filename}'

class Spent(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='spent')
    description = models.CharField(max_length=150)
    price = models.FloatField()
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
