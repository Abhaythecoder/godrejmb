from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- START: Code for temporary DB download ---
import uuid
# Make sure this import points to the views.py file where you added the function
from app.views import secret_db_download_view

# Generate a unique, random path that no one can guess
secret_path = f'download-db-backup-file/{uuid.uuid4()}/'

# This line will print the secret path in your Render deploy logs so you can find it
print(f"SECRET DATABASE DOWNLOAD URL PATH IS: {secret_path}")
# --- END: Code for temporary DB download ---


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