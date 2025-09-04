from django.urls import path
from .views import changePasswordView, editProfileView, loginView, logoutView, registerView, profileView, forgotPasswordView, resetPasswordView

app_name = 'user'

urlpatterns = [
    path('login/', loginView, name='login'),
    path('register/', registerView, name='register'),
    path('logout/', logoutView, name='logout'),
    path('profile/', profileView, name='profile'),
    path('profile/edit/', editProfileView, name='edit_profile'),
    path('change-password/', changePasswordView, name='change_password'),
    path('forgot-password/', forgotPasswordView, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', resetPasswordView, name='reset_password'),
]
