from django.urls import path
from .views import index

app_name = 'web'

urlpatterns = [
    path('', index, name='index'),
]
