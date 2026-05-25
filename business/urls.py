from django.urls import path
from .views import (
    business_list, business_detail, business_edit, business_delete, 
    create_business, business_invitation, business_invitation_form,
    add_income, add_expense, financial_report, business_schedule,
    business_clients, business_items,
    create_business_client, business_client_detail
)

app_name = 'business'

urlpatterns = [
    path('', business_list, name='business_list'),
    path('create/', create_business, name='create_business'),

    # Invitation URLs
    path('invitation/<str:code>/', business_invitation, name='business_invitation'),
    path('invitation/', business_invitation_form, name='business_invitation_form'),

    path('<str:business_name>/schedule/', business_schedule, name='business_schedule'),
    path('<str:business_name>/clients/', business_clients, name='business_clients'),
    path('<str:business_name>/clients/add/', create_business_client, name='create_business_client'),
    path('<str:business_name>/clients/<int:client_id>/', business_client_detail, name='business_client_detail'),
    path('<str:business_name>/items/', business_items, name='business_items'),
    path('edit/<str:business_name>/', business_edit, name='business_edit'),
    path('delete/<str:business_name>/', business_delete, name='business_delete'),

    # Financial URLs
    path('<str:business_name>/add-income/', add_income, name='add_income'),
    path('<str:business_name>/add-expense/', add_expense, name='add_expense'),
    path('<str:business_name>/financial-report/', financial_report, name='financial_report'),
    path('<str:business_name>/', business_detail, name='business_detail'),
]