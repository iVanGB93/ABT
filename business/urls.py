from django.urls import path
from .views import (
    business_list, business_detail, business_edit, business_delete, 
    create_business, business_invitation, business_invitation_form,
    add_income, add_expense, financial_report
)

app_name = 'business'

urlpatterns = [
    path('', business_list, name='business_list'),  
    path('<int:pk>/', business_detail, name='business_detail'),
    path('edit/<int:pk>/', business_edit, name='business_edit'),
    path('delete/<int:pk>/', business_delete, name='business_delete'),
    path('create/', create_business, name='create_business'),
    
    # Financial URLs
    path('<int:pk>/add-income/', add_income, name='add_income'),
    path('<int:pk>/add-expense/', add_expense, name='add_expense'),
    path('<int:pk>/financial-report/', financial_report, name='financial_report'),
    
    # Invitation URLs
    path('invitation/<str:code>/', business_invitation, name='business_invitation'),
    path('invitation/', business_invitation_form, name='business_invitation_form'),
]