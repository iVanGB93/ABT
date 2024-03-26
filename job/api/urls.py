from django.urls import path
from job.api.views import JobsView, ClientsView, JobView, ClientView, ItemView, SpentView

app_name='jobs-api'

urlpatterns = [
    path('list/<str:pk>/', JobsView.as_view(), name="jobs"),
    path('detail/<str:pk>/', JobView.as_view(), name="job_detail"),
    path('create/<str:pk>/', JobView.as_view(), name="job_create"),
    path('update/<str:pk>/', JobView.as_view(), name="job_update"),
    path('delete/<str:pk>/', JobView.as_view(), name="job_delete"),
    path('clients/', ClientsView.as_view(), name="clients"),
    path('client/detail/<str:pk>/', ClientView.as_view(), name="client_detail"),
    path('client/create/<str:pk>/', ClientView.as_view(), name="client_create"),
    path('client/update/<str:pk>/', ClientView.as_view(), name="client_update"),
    path('client/delete/<str:pk>/', ClientView.as_view(), name="client_delete"),
    path('items/list/<str:pk>/', ItemView.as_view(), name="item_list"),
    path('items/used/<str:pk>/', ItemView.as_view(), name="item_used"),
    path('items/create/<str:pk>/', ItemView.as_view(), name="item_create"),
    path('items/update/<str:pk>/', ItemView.as_view(), name="item_update"),
    path('items/delete/<str:pk>/', ItemView.as_view(), name="item_delete"),
    path('spents/list/<str:pk>/', SpentView.as_view(), name="spent_list"),
    path('spents/create/<str:pk>/', SpentView.as_view(), name="spent_create"),
    path('spents/update/<str:pk>/', SpentView.as_view(), name="spent_update"),
    path('spents/delete/<str:pk>/', SpentView.as_view(), name="spent_delete"),
]