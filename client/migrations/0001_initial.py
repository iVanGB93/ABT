# Generated by Django 5.0.2 on 2024-06-11 18:37

import client.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=15)),
                ('last_name', models.CharField(default='no last name saved', max_length=30)),
                ('email', models.EmailField(default='no@email.saved', max_length=80)),
                ('phone', models.CharField(default='no phone saved', max_length=15)),
                ('address', models.CharField(default='no address saved', max_length=150)),
                ('image', models.ImageField(default='userDefault.jpg', upload_to=client.models.upload_to, verbose_name='Image')),
                ('provider', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]