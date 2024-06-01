from django.urls import path
from .views import ItemsView

app_name='item-api'

urlpatterns = [
    path('list/<str:pk>/', ItemsView.as_view(), name='item_list'),
]