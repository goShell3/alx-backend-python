from datetime import datetime, timedelta
import logging
import os
from django.http import HttpResponseForbidden, JsonResponse
from pathlib import Path
from collections import defaultdict

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure logging
log_file = os.path.join(BASE_DIR, 'requests.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Ensure log file exists
        if not os.path.exists(log_file):
            with open(log_file, 'w') as f:
                f.write('Request Log File Created\n')

    def __call__(self, request):
        try:
            # Get the user information
            user = request.user.username if request.user.is_authenticated else 'Anonymous'
            
            # Log the request information
            log_message = f"User: {user} - Path: {request.path}"
            logging.info(log_message)
            
            # Process the request
            response = self.get_response(request)
            
            return response
        except Exception as e:
            logging.error(f"Error in RequestLoggingMiddleware: {str(e)}")
            return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour
        
        # Check if current time is between 9 PM (21) and 6 AM (6)
        if current_hour >= 21 or current_hour < 6:
            return HttpResponseForbidden(
                "Access denied: The messaging service is only available between 6 AM and 9 PM."
            )
        
        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Dictionary to store request counts for each IP
        self.request_counts = defaultdict(list)
        # Maximum number of messages allowed per time window
        self.max_requests = 5
        # Time window in seconds (1 minute)
        self.time_window = 60

    def __call__(self, request):
        # Only check POST requests to message endpoints
        if request.method == 'POST' and 'messages' in request.path:
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()

            # Clean up old requests outside the time window
            self.cleanup_old_requests(ip_address, current_time)

            # Check if the IP has exceeded the rate limit
            if len(self.request_counts[ip_address]) >= self.max_requests:
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'message': f'You can only send {self.max_requests} messages per minute. Please wait before sending more messages.'
                }, status=429)

            # Add the current request to the count
            self.request_counts[ip_address].append(current_time)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def cleanup_old_requests(self, ip_address, current_time):
        # Remove requests older than the time window
        self.request_counts[ip_address] = [
            req_time for req_time in self.request_counts[ip_address]
            if (current_time - req_time).total_seconds() <= self.time_window
        ]

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Define admin-only paths
        self.admin_paths = [
            '/api/admin/',
            '/api/users/delete/',
            '/api/messages/delete/',
            '/api/conversations/delete/'
        ]
        # Define moderator-only paths
        self.moderator_paths = [
            '/api/messages/moderate/',
            '/api/users/moderate/'
        ]

    def __call__(self, request):
        # Skip check for non-authenticated users (they'll be handled by authentication middleware)
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get the current path
        current_path = request.path

        # Check if the path requires admin privileges
        if any(path in current_path for path in self.admin_paths):
            if not request.user.is_staff:  # Django's built-in admin check
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': 'This action requires administrator privileges.'
                }, status=403)

        # Check if the path requires moderator privileges
        if any(path in current_path for path in self.moderator_paths):
            if not (request.user.is_staff or hasattr(request.user, 'is_moderator')):
                return JsonResponse({
                    'error': 'Permission denied',
                    'message': 'This action requires moderator privileges.'
                }, status=403)

        return self.get_response(request) 