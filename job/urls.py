from django.urls import path
from .views import job_list, invoice_detail, create_job, job_detail, delete_job, create_spent, spent_detail, close_job, client_list, create_client, client_detail, delete_spent, soon

app_name = 'job'

urlpatterns = [
    path('', job_list, name='job_list'),
    path('soon/', soon, name='soon'),
    path('create/', create_job, name='create_job'),
    path('client/list/', client_list, name='client_list'),
    path('client/create/', create_client, name='create_client'),
    path('client/detail/<int:id>/', client_detail, name='client_detail'),
    path('detail/<int:id>/', job_detail, name='job_detail'),
    path('delete/<int:id>/', delete_job, name='delete_job'),
    path('close/<int:id>/', close_job, name='close_job'),
    path('create/spent/<int:id>/', create_spent, name='create_spent'),
    path('detail/spent/<int:id>/', spent_detail, name='spent_detail'),
    path('delete/spent/<int:id>/', delete_spent, name='delete_spent'),
    path('invoice/<str:number>/', invoice_detail, name='invoice_detail'),
]
