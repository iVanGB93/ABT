# Generated by Django 5.0.2 on 2024-07-30 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0016_alter_invoice_bill_to_alter_invoice_job_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spent',
            name='job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='spent', to='job.job'),
        ),
    ]
