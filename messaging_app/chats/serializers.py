from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password', 'profile_picture', 'bio', 'phone_number', 'is_online', 'last_seen', 'status']

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'created_at', 'updated_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['participants'] = UserSerializer(instance.participants.all(), many=True).data
        return data

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'sent_at', 'is_read']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = UserSerializer(instance.sender).data
        return data

        
