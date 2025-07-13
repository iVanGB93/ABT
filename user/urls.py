from django.urls import path
from .views import loginView, logoutView, registerView

app_name = 'user'

urlpatterns = [
    path('login/', loginView, name='login'),
    path('register/', registerView, name='register'),
    path('logout/', logoutView, name='logout'),
]
