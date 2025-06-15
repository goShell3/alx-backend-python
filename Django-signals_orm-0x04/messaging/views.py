from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def delete_user(request):
    user = request.user
    logout(request)  # Log out before deleting the user
    user.delete()
    messages.success(request, "Your account and associated data have been deleted.")
    return redirect("home")  # Replace "home" with your landing page
