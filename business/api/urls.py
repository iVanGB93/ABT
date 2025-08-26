from django.urls import path
from .views import BusinessesView, BusinessView, ExtrasView, PaymentMethodTypeView, PaymentMethodView

app_name = 'business-api'

urlpatterns = [
    path('<str:pk>/', BusinessesView.as_view(), name='businesses_list'),
    path('create/<str:pk>/', BusinessView.as_view(), name='business_create'),
    path('update/<str:pk>/', BusinessView.as_view(), name='business_update'),
    path('delete/<str:pk>/', BusinessView.as_view(), name='business_delete'),
    path('extras/<str:pk>/', ExtrasView.as_view(), name='extras'),

    path('payment-methods/types/', PaymentMethodTypeView.as_view(), name='payment_method_types'),
    path('<str:pk>/payment-methods/', PaymentMethodView.as_view(), name='payment_methods'),
    path('<str:pk>/payment-methods/<str:payment_method_id>/', PaymentMethodView.as_view(), name='payment_method_update'),
    path('<str:pk>/payment-methods/<str:payment_method_id>/', PaymentMethodView.as_view(), name='payment_method_delete'),
]
