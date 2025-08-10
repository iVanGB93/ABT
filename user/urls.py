from django.urls import path
from .views import changePasswordView, editProfileView, loginView, logoutView, registerView, profileView 

app_name = 'user'

urlpatterns = [
    path('login/', loginView, name='login'),
    path('register/', registerView, name='register'),
    path('logout/', logoutView, name='logout'),
    path('profile/', profileView, name='profile'),
    path('profile/edit/', editProfileView, name='edit_profile'),
    path('change-password/', changePasswordView, name='change_password')
]
