from django.contrib import admin
from .models import Spent, Job, Invoice

admin.site.register(Job)
admin.site.register(Spent)
admin.site.register(Invoice)
