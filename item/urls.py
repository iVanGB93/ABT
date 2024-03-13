from django.urls import path
from .views import items_list, create_item, item_detail

app_name = 'item'

urlpatterns = [
    path('', items_list, name='items_list'),
    path('detail/<int:id>/', item_detail, name='item_detail'),
    path('create/', create_item, name='create_item'),
]
