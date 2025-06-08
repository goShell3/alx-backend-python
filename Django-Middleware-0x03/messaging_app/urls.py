from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('chats.urls')),  # Include the chat app's URLs
    path('api-auth/', include('rest_framework.urls')),  # DRF auth URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
