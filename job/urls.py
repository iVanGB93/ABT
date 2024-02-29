from django.urls import path
from .views import job_list, create_job, job_detail, delete_job, create_spent, spent_detail, close_job

app_name = 'job'

urlpatterns = [
    path('', job_list, name='job_list'),
    path('create/', create_job, name='create_job'),
    path('detail/<int:id>/', job_detail, name='job_detail'),
    path('delete/<int:id>/', delete_job, name='delete_job'),
    path('close/<int:id>/', close_job, name='close_job'),
    path('create/spent/<int:id>/', create_spent, name='create_spent'),
    path('detail/spent/<int:id>/', spent_detail, name='spent_detail'),
]
