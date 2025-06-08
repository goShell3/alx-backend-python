from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView



class UserCanReadonly(BasePermission):
    def has_permission(self, request, view):
        return request.has_permission(request, view)
    
class UserCanViewMessage(APIView):
    permission_classes = [IsAuthenticated|UserCanReadonly]

    def get(self, request, format=None):
        content = {
            'status': 'request was permitted'
        }
        return Response(content)
    