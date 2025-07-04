from django.urls import path
from .views import business_list, business_detail

app_name = 'business'

urlpatterns = [
    path('', business_list, name='business_list'),  
    path('<int:business_id>/', business_detail, name='business_detail'),
]