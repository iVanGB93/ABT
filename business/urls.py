from django.urls import path
from .views import business_list, business_detail, business_invitation, business_invitation_form

app_name = 'business'

urlpatterns = [
    path('', business_list, name='business_list'),  
    path('<int:business_id>/', business_detail, name='business_detail'),
    path('<int:business_id>/', business_detail, name='business_detail'),
    path('invitation/<str:code>/', business_invitation, name='business_invitation'),
    path('invitation/', business_invitation_form, name='business_invitation_form'),
]