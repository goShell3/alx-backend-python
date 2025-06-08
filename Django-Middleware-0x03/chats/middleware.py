from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        
        # Log the request information
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response 