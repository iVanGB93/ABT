from django.urls import path
from .views import ClientsView, ClientView

app_name = 'client-api'

urlpatterns = [
    path('<str:pk>/', ClientsView.as_view(), name='client_list'),
    path('create/<str:pk>/', ClientView.as_view(), name='client_create'),
    path('update/<str:pk>/', ClientView.as_view(), name='client_update'),
    path('delete/<str:pk>/', ClientView.as_view(), name='client_delete'),
]
