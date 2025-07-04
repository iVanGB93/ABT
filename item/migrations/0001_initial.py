# Generated by Django 5.0.2 on 2024-03-13 16:58

import django.db.models.deletion
import django.db.models.functions.datetime
import item.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('job', '0008_alter_job_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=150)),
                ('price', models.IntegerField()),
                ('used', models.BooleanField(default=False)),
                ('image', models.ImageField(default='itemDefault.jpg', upload_to=item.models.upload_to_item)),
                ('date', models.DateTimeField(db_default=django.db.models.functions.datetime.Now())),
                ('spent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='job.spent')),
            ],
        ),
    ]
