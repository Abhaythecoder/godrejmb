from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Add the secret path to your url patterns
    path(secret_path, secret_db_download_view, name='secret_db_download'),
    
    # Your existing paths
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)