from django.urls import include, path

app_name = 'schedule'

urlpatterns = [
    path('', include('schedule.api.urls')),
]
