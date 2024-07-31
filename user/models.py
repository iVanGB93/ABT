from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.db import models
from django.utils.crypto import get_random_string
from django.db.models.functions import Now


def upload_to(instance, filename):
    return 'user/{filename}'.format(filename=filename)

def upload_logo_to(instance, filename):
    return 'logo/{filename}'.format(filename=filename)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='-')
    address = models.CharField(max_length=150, default='-')
    image = models.ImageField(_("Image"), upload_to=upload_to, default='userDefault.jpg')
    business_name = models.CharField(max_length=150, default='Business Name')
    business_logo = models.ImageField(_("Image"), upload_to=upload_logo_to, default='logoDefault.png')
    is_client = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
           output_size = (300, 300)
           img.thumbnail(output_size)
           img.save(self.image.path)


def generarHash():    
    while True:
        code = get_random_string(length=6, allowed_chars="1234567890")
        if RegistrationCode.objects.filter(code=code).count() == 0:
            break
    return code

class RegistrationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    email=models.EmailField()
    code=models.IntegerField(default=generarHash, unique=True)
    dateStart = models.DateTimeField(db_default=Now())
    dateEnd = models.DateTimeField(null=True)

    def __str__(self):
        return self.email