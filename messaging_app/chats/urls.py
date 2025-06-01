from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Additional endpoints for specific actions
    path('conversations/<int:pk>/send_message/', 
         MessageViewSet.as_view({'post': 'create'}), 
         name='conversation-send-message'),
    path('conversations/<int:pk>/messages/', 
         MessageViewSet.as_view({'get': 'list'}), 
         name='conversation-messages'),
] 