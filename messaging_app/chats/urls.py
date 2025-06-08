from django.urls import path, include
from rest_framework_nested import routers
from .views import UserViewSet, ConversationViewSet, MessageViewSet, RegistrationView

# Create the main router
router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Create a nested router for messages
conversations_router = routers.NestedDefaultRouter(
    router, r'conversations', lookup='conversation'
)
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
