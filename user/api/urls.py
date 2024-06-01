from django.urls import path
from .views import RegisterView, ClientsView, ClientView

app_name='user-api'

urlpatterns = [
    path('clients/<str:pk>/', ClientsView.as_view(), name='client_list'),
    path('client/create/<str:pk>/', ClientView.as_view(), name='client_create'),
    path('client/update/<str:pk>/', ClientView.as_view(), name='client_update'),
    path('client/delete/<str:pk>/', ClientView.as_view(), name='client_delete'),
    path('register/', RegisterView.as_view(), name='register'),
]