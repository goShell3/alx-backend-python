from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from models import Message

@login_required
def delete_user(request):
    user = request.user
    logout(request)  # Log out before deleting the user
    user.delete()
    messages.success(request, "Your account and associated data have been deleted.")
    return redirect("home")  # Replace "home" with your landing page


def conversation_view(request):
    messages = Message.objects.filter(parent_message__isnull=True).select_related(
        'sender'
    ).prefetch_related(
        'replies__sender',
        'replies__replies__sender',  # Prefetch deeper levels if needed
    )

    threads = [build_thread(msg) for msg in messages]

    return render(request, 'conversation.html', {'threads': threads})