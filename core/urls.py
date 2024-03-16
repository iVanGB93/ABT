from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('items/', include('item.urls')),
    path('jobs/', include('job.urls')),
    path('api/jobs/', include('job.api.urls')),
    path('user/', include('user.urls')),
    path('', include('web.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)