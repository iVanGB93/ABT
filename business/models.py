from django.db import models
from django.contrib.auth.models import User

def upload_to_business(instance, filename):
    return 'businesses/{filename}'.format(filename=filename)

class Business(models.Model):
    owners = models.ManyToManyField(User, related_name='businesses')
    name = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to=upload_to_business, default='logoDefault.jpg')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'
        ordering = ['name']
