from django.urls import path
from .views import items_list, create_item, item_detail, delete_item

app_name = 'item'

urlpatterns = [
    path('', items_list, name='items_list'),
    path('detail/<int:id>/', item_detail, name='item_detail'),
    path('delete/<int:id>/', delete_item, name='delete_item'),
    path('create/', create_item, name='create_item'),
]
