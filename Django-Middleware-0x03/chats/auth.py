from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UserMessageView(APIView):
    authentication_classes = [BaseAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  
            'auth': str(request.auth), 
        }
        
        return Response(content)