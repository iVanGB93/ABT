from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('items/', include('item.urls')),
    path('api/items/', include('item.api.urls')),
    path('jobs/', include('job.urls')),
    path('api/jobs/', include('job.api.urls')),
    path('business/', include('business.urls')),
    path('api/business/', include('business.api.urls')),
    path('api/clients/', include('client.api.urls')),
    path('user/', include('user.urls')),
    path('api/user/', include('user.api.urls')),
    path('', include('web.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)