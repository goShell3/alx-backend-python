from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from chats.views import ConversationViewSet, MessageViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),  # Include the router's URLs
    path('api-auth/', include('rest_framework.urls')),  # DRF auth URLs
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
