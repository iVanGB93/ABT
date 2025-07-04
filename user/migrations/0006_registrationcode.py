# Generated by Django 5.0.2 on 2024-07-30 19:42

import django.db.models.deletion
import django.db.models.functions.datetime
import user.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_profile_business_logo_profile_business_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('code', models.IntegerField(default=user.models.generarHash, unique=True)),
                ('dateStart', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('dateEnd', models.DateTimeField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
