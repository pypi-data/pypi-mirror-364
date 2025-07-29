import time
import logging

from django.conf import settings
from rest_framework import status
from django.db import connections
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest

from django_rds_iam_auth.middleware.jwt_exposer import local
from django_rds_iam_auth.utils import is_connection_valid, create_connection
from django_rds_iam_auth.aws.utils.aws_access_heper import CredentialsManager

# Configure logger for this module
logger = logging.getLogger(__name__)


class ConnectionInjectorMiddleware:
    """
    Django middleware that dynamically injects RDS IAM-authenticated database connections
    based on user context stored in thread-local storage.

    This middleware:
    1. Cleans thread-local storage before processing each request
    2. Creates user-specific database connections using AWS IAM credentials
    3. Handles connection failures and retries
    4. Ensures thread-local storage is cleaned after each request

    Attributes:
        get_response: The next middleware or view function in the Django request chain
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the next response handler.

        Args:
            get_response: The next middleware or view function in the chain
        """
        self.get_response = get_response
        logger.info("ConnectionInjector middleware initialized")

    def __call__(self, request):
        """
        Process incoming request and inject dynamic database connection if needed.

        This method:
        1. Checks if user authentication is present (no need to clean as previous middleware handles it)
        2. Creates or reuses database connections
        3. Handles connection errors gracefully
        4. Ensures cleanup after processing

        Args:
            request: The incoming Django request object

        Returns:
            HttpResponse: The response from the next middleware/view or error response
        """
        logger.debug(f"Processing connection injection for path: {request.path}")

        # Get user_id from thread-local storage (set by previous middleware)
        user_id = getattr(local, 'user_id', None)

        # If no user_id in local storage, skip dynamic connection setup
        if user_id is None:
            logger.debug("No user_id found in local storage, skipping dynamic connection")
            return self.get_response(request)

        try:
            # Check if connection already exists and is still valid
            if connections.databases.get(user_id) and is_connection_valid(user_id):
                logger.debug(f"Reusing existing connection for user: {user_id}")
                return self.get_response(request)

            logger.info(f"Creating new dynamic database connection for user: {user_id}")

            # Create a copy of default database configuration
            dynamic_database = connections.databases['default'].copy()

            # Get required tokens from thread-local storage
            access_token = getattr(local, 'access_token', None)
            id_token = getattr(local, 'id_token', None)
            id_token_payload = getattr(local, 'id_token_payload', None)

            if not all([access_token, id_token, id_token_payload]):
                logger.error(f"Missing required tokens for user {user_id}")
                return self.error_response("Missing authentication tokens")

            # Initialize credentials manager with tokens from local storage
            cred_manager = CredentialsManager(
                access_token=access_token,
                id_token=id_token,
                id_token_payload=id_token_payload,
            )

            # Get AWS credentials and store in local storage
            credentials = cred_manager.get_credentials()
            local.credentials = credentials
            logger.debug(f"Retrieved AWS credentials for user: {user_id}")

            # Create and register the dynamic database connection
            connections.databases[user_id] = create_connection(
                dynamic_database, user_id, credentials
            )

            # Verify connection is working, retry once if needed
            if not is_connection_valid(user_id):
                logger.warning(f"Initial connection failed for user: {user_id}, retrying...")

                # Wait for connection establishment and retry with fresh credentials
                reconnection_timeout = getattr(settings, 'DYNAMIC_CONNECTION_RETRY_TIMEOUT', 0.1)
                time.sleep(reconnection_timeout)
                cred_manager.reset_credentials()
                credentials = cred_manager.get_credentials()
                local.credentials = credentials

                connections.databases[user_id] = create_connection(
                    dynamic_database, user_id, credentials
                )

                # Raise exception if connection still fails
                is_connection_valid(user_id, raise_exception=True)
                logger.info(f"Successfully reconnected for user: {user_id}")
            else:
                logger.info(f"Successfully connected for user: {user_id}")

        except Exception as e:
            logger.error(f"Failed to create RDS connection for user {user_id}: {str(e)}", exc_info=True)
            return self.error_response(f'Failed to create rds connection.')

        # Process the request with the dynamic connection
        response = self.get_response(request)
        logger.debug(f"Request processing completed for user: {user_id}")

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
        logger.error(f"Exception occurred during request processing: {str(exception)}", exc_info=True)
        local.__dict__.clear()

    @staticmethod
    def error_response(error_message: str) -> JsonResponse:
        """
        Create a standardized error response for connection failures.

        Args:
            error_message: The error message to include in the response

        Returns:
            JsonResponse: A JSON response with error details and 400 status code
        """
        logger.warning(f"Returning error response: {error_message}")
        return JsonResponse(
            data={'detail': error_message},
            status=status.HTTP_400_BAD_REQUEST
        )
