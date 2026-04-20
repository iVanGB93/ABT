from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.db import models
from django.utils.crypto import get_random_string
from django.db.models.functions import Now
from io import BytesIO
import os

def upload_to(instance, filename):
    filename = os.path.basename(filename)
    return f'user/{instance.user.username}/{filename}'

def upload_logo_to(instance, filename):
    filename = os.path.basename(filename)
    return f'logo/{instance.user.username}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, default='')
    address = models.CharField(max_length=150, default='')
    image = models.ImageField(_("Image"), upload_to=upload_to, default='userDefault.jpg')
    is_client = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            self.image.open()
            img = Image.open(self.image)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                buffer = BytesIO()
                img.save(buffer, format=img.format)
                buffer.seek(0)
                self.image.save(self.image.name, buffer, save=False)
                super().save(*args, **kwargs)


def generarHash():    
    while True:
        code = get_random_string(length=6, allowed_chars="1234567890")
        if RegistrationCode.objects.filter(code=code).count() == 0:
            break
    return code

class RegistrationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    email=models.EmailField()
    code=models.CharField(max_length=6, default=generarHash, unique=True)
    created = models.DateTimeField(db_default=Now())
    active = models.BooleanField(default=True)
    used = models.DateTimeField(null=True)


    def __str__(self):
        return self.email