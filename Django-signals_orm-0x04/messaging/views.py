from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from models import Message
from django.shortcuts import render

@login_required
def delete_user(request):
    user = request.user
    logout(request)  # Log out before deleting the user
    user.delete()
    messages.success(request, "Your account and associated data have been deleted.")
    return redirect("home")  # Replace "home" with your landing page

@login_required
def unread_inbox_view(request):
    unread_messages = Message.unread.for_user(request.user)

    return render(request, 'inbox/unread_messages.html', {
        'unread_messages': unread_messages
    })

def conversation_view(request):
    messages = Message.objects.filter(parent_message__isnull=True).select_related(
        'sender'
    ).prefetch_related(
        'replies__sender',
        'replies__replies__sender',  # Prefetch deeper levels if needed
    )

    threads = [build_thread(msg) for msg in messages]

    return render(request, 'conversation.html', {'threads': threads})

@login_required
def message_thread_view(request):
    user = request.user

    messages = Message.objects.filter(
        parent_message__isnull=True
    ).filter(
        models.Q(sender=user) | models.Q(recipient=user)  # Filtering by sender or receiver
    ).select_related(
        'sender', 'recipient'
    ).prefetch_related(
        'replies__sender', 'replies__recipient'
    )

    return render(request, 'messaging/message_threads.html', {
        'messages': messages
    })