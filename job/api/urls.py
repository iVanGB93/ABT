from django.urls import path
from job.api.views import JobsView, ClientsView, JobView, ClientView

app_name='jobs-api'

urlpatterns = [
    path('', JobsView.as_view(), name="jobs"),
    path('<int:pk>/', JobView.as_view(), name="job"),
    path('clients/', ClientsView.as_view(), name="clients"),
    path('clients/<int:pk>/', ClientView.as_view(), name="client"),
]