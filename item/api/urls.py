from django.urls import path
from .views import ItemsView, SpentsView

app_name='item-api'

urlpatterns = [
    path('list/<str:pk>/', ItemsView.as_view(), name='item_list'),
    path('create/<str:pk>/', ItemsView.as_view(), name="item_create"),
    path('update/<str:pk>/', ItemsView.as_view(), name="item_update"),
    path('used/<str:pk>/', SpentsView.as_view(), name="item_used"),
    path('delete/<str:pk>/', ItemsView.as_view(), name="item_delete"),
]