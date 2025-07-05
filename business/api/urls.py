from django.urls import path
from .views import BusinessesView, BusinessView

app_name = 'business-api'

urlpatterns = [
    path('<str:pk>/', BusinessesView.as_view(), name='businesses_list'),
    path('create/<str:pk>/', BusinessView.as_view(), name='business_create'),
    path('update/<str:pk>/', BusinessView.as_view(), name='business_update'),
    path('delete/<str:pk>/', BusinessView.as_view(), name='business_delete'),
]
