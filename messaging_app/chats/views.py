from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

# current modules 
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.
    Provides CRUD operations for users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_seen']

    def get_queryset(self):
        """Return users based on query parameters."""
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        if username:
            queryset = queryset.filter(username__icontains=username)
        return queryset

    @action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        """Get all conversations for a specific user."""
        user = self.get_object()
        conversations = user.conversations.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model.
    Provides CRUD operations for conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['participants']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        """Return conversations for the current user."""
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        """Create a new conversation with the current user as a participant."""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        return conversation

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        if user in conversation.participants.all():
            return Response(
                {'error': 'User is already a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conversation.participants.add(user)
        return Response(
            {'status': 'participant added'}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from the conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        user = get_object_or_404(User, id=user_id)
        if user not in conversation.participants.all():
            return Response(
                {'error': 'User is not a participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if conversation.participants.count() <= 1:
            return Response(
                {'error': 'Cannot remove the last participant'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conversation.participants.remove(user)
        return Response(
            {'status': 'participant removed'},
            status=status.HTTP_200_OK
        )

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model.
    Provides CRUD operations for messages within conversations.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sender', 'is_read']
    ordering_fields = ['sent_at']

    def get_queryset(self):
        """Return messages for the current conversation."""
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(
            conversation_id=conversation_id,
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def perform_create(self, serializer):
        """Create a new message in the current conversation."""
        conversation_id = self.kwargs.get('conversation_pk')
        conversation = get_object_or_404(
            Conversation, 
            id=conversation_id,
            participants=self.request.user
        )
        serializer.save(
            sender=self.request.user,
            conversation=conversation
        )

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read."""
        message = self.get_object()
        message.is_read = True
        message.save()
        return Response(
            {'status': 'message marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def unread_count(self, request, conversation_pk=None):
        """Get count of unread messages in conversation."""
        queryset = self.get_queryset().filter(is_read=False)
        count = queryset.exclude(sender=request.user).count()
        return Response({'unread_count': count})