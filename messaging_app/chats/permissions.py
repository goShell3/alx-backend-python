from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# models
from .models import Conversation


class UserCanReadonly(BasePermission):
    def has_permission(self, request, view):
        return request.has_permission(request, view)
    
class IsParticipantOfConversation(BasePermission):
    
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            self.message = "HTTP_403_FORBIDDEN - Authentication required"
            return False 
        
        if view.action in ['list', 'create']:
            return True
        
        if view.action ['retrieve', 'update', 'partial_update', 'destroy', "PUT", "PATCH", "DELETE"]:
            conversation_id = view.kwargs.get('pk')
            try:
                conversation = Conversation.objects.get(id=conversation_id)
                return request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        return False
    
class UserCanViewMessage(APIView):
    permission_classes = [IsAuthenticated|UserCanReadonly]

    def get(self, request, format=None):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)
    