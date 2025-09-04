from django.urls import path
from .views import RegisterView, AccountView, ForgotPasswordView

app_name='user-api'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('account/<str:pk>/', AccountView.as_view(), name='account'),
    path('account/update/<str:pk>/', AccountView.as_view(), name='account'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
]