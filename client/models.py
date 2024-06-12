from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.db import models

def upload_to(instance, filename):
    return 'client/{filename}'.format(filename=filename)

class Client(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=30, default='no last name saved')
    email = models.EmailField(max_length=80, default='no@email.saved')
    phone = models.CharField(max_length=15, default='no phone saved')
    address = models.CharField(max_length=150, default='no address saved')
    image = models.ImageField(_("Image"), upload_to=upload_to, default='userDefault.jpg')

    def __str__(self):
        return self.provider.username + self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
           output_size = (300, 300)
           img.thumbnail(output_size)
           img.save(self.image.path)