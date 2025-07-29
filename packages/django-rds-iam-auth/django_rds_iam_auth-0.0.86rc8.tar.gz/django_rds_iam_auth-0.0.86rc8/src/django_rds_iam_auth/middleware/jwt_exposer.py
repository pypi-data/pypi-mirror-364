import threading
import logging

from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest

# Configure logger for this module
logger = logging.getLogger(__name__)

# Thread-local storage for request-scoped data
# This object stores JWT tokens and user context that should be isolated per thread
local = threading.local()


class JWTExposerMiddleware:
    """
    Django middleware that extracts and exposes JWT tokens from HTTP headers
    to thread-local storage for use throughout the request lifecycle.

    This middleware:
    1. Cleans thread-local storage before processing each request
    2. Extracts JWT tokens and organization ID from HTTP headers
    3. Stores extracted data in thread-local storage for downstream middleware/views
    4. Ensures thread-local storage is cleaned after each request

    Expected HTTP Headers:
        - Authorization: Bearer token (access token)
        - IdToken: JWT ID token
        - OrganizationId: Organization identifier

    Thread-local variables set:
        - access_token: Extracted access token (Bearer prefix removed)
        - id_token: JWT ID token
        - organization_id: Organization identifier
        - account_id: AWS account ID from settings
        - user_id: Initially None, set by downstream middleware
        - id_token_payload: Initially None, decoded token payload
        - access_token_payload: Initially None, decoded token payload
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the next response handler.

        Args:
            get_response: The next middleware or view function in the chain
        """
        self.get_response = get_response
        logger.info("JWTExposer middleware initialized")

    def __call__(self, request: WSGIRequest, *args, **kwargs):
        """
        Process incoming request and extract JWT tokens to thread-local storage.

        This method:
        1. Cleans thread-local storage before processing
        2. Extracts JWT tokens and metadata from HTTP headers
        3. Stores extracted data in thread-local storage
        4. Processes the request through the chain
        5. Ensures cleanup after processing

        Args:
            request: The incoming Django request object
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: The response from the next middleware/view
        """
        # Clean thread-local storage before processing new request
        local.__dict__.clear()
        logger.debug(f"Processing JWT extraction for request: {request.path}")

        # Extract JWT tokens and metadata from HTTP headers
        # HTTP headers are prefixed with HTTP_ in Django's request.META
        local.access_token = request.META.get('HTTP_AUTHORIZATION', None)
        local.id_token = request.META.get('HTTP_IDTOKEN', None)

        # Clean up Bearer prefix from access token if present
        if local.access_token and local.access_token.startswith("Bearer "):
            local.access_token = str.replace(local.access_token, 'Bearer ', '')
            logger.debug("Removed 'Bearer ' prefix from access token")

        # Set AWS account ID from Django settings
        local.account_id = getattr(settings, 'AWS_ACCOUNT_ID', None)
        if not local.account_id:
            logger.warning("AWS_ACCOUNT_ID not found in settings")

        local.identity_pool_id = request.META.get('HTTP_IPI', None)
        local.user_pool_id = request.META.get('HTTP_UPI', None)

        # Process request through the middleware chain
        response = self.get_response(request)

        # Clean thread-local storage after processing
        local.__dict__.clear()
        logger.debug("Request processing completed, thread-local storage cleaned")

        return response

    def process_exception(self, request: WSGIRequest, exception: Exception) -> None:
        """
        Handle exceptions and ensure thread-local storage is cleaned.

        This method is called by Django when an unhandled exception occurs
        during request processing, ensuring cleanup happens even in error scenarios.

        Args:
            request: The Django request object
            exception: The exception that occurred
        """
        logger.error(f"Exception occurred during JWT processing: {str(exception)}", exc_info=True)
        local.__dict__.clear()
