from datetime import datetime
import logging
import os
from django.http import HttpResponseForbidden
from pathlib import Path

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