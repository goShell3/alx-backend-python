from django.contrib import admin
from .models import Message, MessageHistory

class MessageHistoryInline(admin.TabularInline):
    model = MessageHistory
    extra = 0
    readonly_fields = ("old_content", "edited_at")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "content", "edited", "timestamp")
    inlines = [MessageHistoryInline]

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ("message", "edited_at", "old_content")
