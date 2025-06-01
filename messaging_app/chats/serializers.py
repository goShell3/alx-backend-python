from rest_framework import serializers
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile_picture', 
                 'bio', 'phone_number', 'is_online', 'last_seen', 'status']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'last_message', 'created_at', 'updated_at']

    def get_participants(self, obj):
        return UserSerializer(obj.participants.all(), many=True).data

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    conversation = serializers.CharField(source='conversation.id')

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'message_body', 
                 'sent_at', 'is_read']
        read_only_fields = ['sent_at', 'is_read']

    def get_sender(self, obj):
        return UserSerializer(obj.sender).data

    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Message is too long")
        return value