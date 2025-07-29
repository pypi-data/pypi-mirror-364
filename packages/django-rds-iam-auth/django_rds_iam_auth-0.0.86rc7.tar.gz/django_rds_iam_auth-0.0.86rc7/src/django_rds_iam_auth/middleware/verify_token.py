import json
import logging
from typing import Union

import jwt
import requests
from django.urls import resolve
from django.conf import settings
from rest_framework import status
from django.core.cache import caches
from django.http import JsonResponse
from django.core.handlers.wsgi import WSGIRequest

from django_rds_iam_auth.middleware.jwt_exposer import local

# Configure logger for this module
logger = logging.getLogger(__name__)


class VerifyTokenMiddleware:
    """
    Django middleware that verifies JWT tokens and extracts user information.

    This middleware:
    1. Cleans thread-local storage before and after processing
    2. Determines if token verification is required based on route configuration
    3. Verifies JWT tokens using JWKS (JSON Web Key Set) from AWS Cognito
    4. Extracts and validates token payloads
    5. Handles various token-related errors with appropriate HTTP responses
    6. Caches JWKS keys for performance optimization

    The middleware supports:
    - Access token verification and payload extraction
    - ID token verification with audience validation
    - Route-based security (secure vs non-secure routes)
    - JWKS key caching with automatic refresh
    - Comprehensive error handling for various JWT validation failures
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the next response handler.

        Args:
            get_response: The next middleware or view function in the chain
        """
        self.get_response = get_response
        logger.info("VerifyToken middleware initialized")

    def __call__(self, request):
        """
        Process incoming request and verify JWT tokens if required.

        This method:
        1. Cleans thread-local storage before processing
        2. Determines if verification is needed based on route configuration
        3. Verifies tokens and extracts user information
        4. Handles token validation errors
        5. Ensures cleanup after processing

        Args:
            request: The incoming Django request object

        Returns:
            HttpResponse: The response from the next middleware/view or error response
        """
        view_name = resolve(request.path_info).url_name
        logger.debug(f"Processing token verification for route: {view_name} (path: {request.path})")

        if self.is_verification_required(request):
            logger.debug(f"Token verification required for route: {view_name}")
            try:
                # Execute pre-decoding hooks
                self.pre_token_decoding_trigger(request)

                # Decode and verify access token
                logger.debug("Decoding access token")
                local.access_token_payload = self.decode_token(local.access_token)

                # Extract client ID for ID token verification
                client_id = local.access_token_payload['client_id']
                logger.debug(f"Using client_id: {client_id} for ID token verification")

                # Decode and verify ID token with audience validation
                logger.debug("Decoding ID token")
                local.id_token_payload = self.decode_token(local.id_token, client_id)

                # Extract user ID from access token
                local.user_id = local.access_token_payload['sub']
                logger.info(f"Successfully verified tokens for user: {local.user_id}")

                # Execute post-decoding hooks
                self.post_token_decoding_trigger(request)

            except jwt.InvalidTokenError as e:
                logger.warning(f"JWT validation failed: {e.args[0]}")
                # Handle specific JWT validation errors
                if e.args[0] == 'Signature verification failed':
                    return self.invalid_token_response()
                elif e.args[0] == 'Signature has expired':
                    return self.token_expire_response()
                elif e.args[0] == 'Invalid payload padding':
                    return self.invalid_padding_response()
                elif e.args[0] == 'Invalid crypto padding':
                    return self.invalid_crypto_padding_response()
                elif e.args[0] in ('Invalid audience', "Audience doesn't match"):
                    return self.invalid_audience_response()
                elif e.args[0] == 'Not enough segments':
                    return self.not_enough_segments()
                return self.failed_verify_response()
            except Exception as e:
                logger.error(f"Unexpected error during token verification: {str(e)}", exc_info=True)
                return self.failed_verify_response()
        elif view_name not in getattr(settings, 'NON_SECURE_ROUTES', tuple()):
            # Check for missing tokens on secure routes
            logger.debug(f"Checking token presence for secure route: {view_name}")
            if not getattr(local, 'access_token', None) and not getattr(local, 'id_token', None):
                logger.warning(f"Both tokens missing for secure route: {view_name}")
                return self.tokens_are_missing_response()
            elif not getattr(local, 'access_token', None):
                logger.warning(f"Access token missing for secure route: {view_name}")
                return self.access_token_is_missing_response()
            elif not getattr(local, 'id_token', None):
                logger.warning(f"ID token missing for secure route: {view_name}")
                return self.id_token_is_missing_response()
        else:
            # Clear tokens for non-secure routes
            logger.debug(f"Non-secure route detected: {view_name}, clearing tokens")
            local.__dict__.clear()

        # Process request through the middleware chain
        response = self.get_response(request)

        # Clean thread-local storage after processing
        local.__dict__.clear()
        logger.debug("Token verification completed, thread-local storage cleaned")

        return response

    def is_verification_required(self, request) -> bool:
        url_name = resolve(request.path_info).url_name
        return bool(
            not hasattr(settings, 'NON_SECURE_ROUTES') or url_name not in settings.NON_SECURE_ROUTES
            and not request.path_info.startswith('/admin')
            and not request.path_info.startswith('/manufacture')
        )

    def pre_token_decoding_trigger(self, request):
        """
        Hook method called before token decoding begins.

        This method can be overridden in subclasses to perform custom logic
        before JWT tokens are decoded and verified.

        Args:
            request: The Django request object
        """
        logger.debug("Pre-token decoding trigger executed")
        pass

    def post_token_decoding_trigger(self, request):
        """
        Hook method called after successful token decoding.

        This method can be overridden in subclasses to perform custom logic
        after JWT tokens have been successfully decoded and verified.

        Args:
            request: The Django request object
        """
        logger.debug("Post-token decoding trigger executed")
        pass

    def process_exception(self, request: WSGIRequest, exception: Exception) -> None:
        """
        Handle exceptions and ensure thread-local storage is cleaned.

        Args:
            request: The Django request object
            exception: The exception that occurred
        """
        logger.error(f"Exception occurred during token verification: {str(exception)}", exc_info=True)
        local.__dict__.clear()

    @staticmethod
    def cache_jwks_keys():
        """
        Fetch and cache JWKS (JSON Web Key Set) keys from AWS Cognito.

        This method retrieves all public keys from the JWKS endpoint and caches
        them individually by their key ID (kid) for 1 hour. These keys are used
        to verify JWT token signatures.

        Raises:
            Exception: If unable to fetch keys from the JWKS endpoint
        """
        logger.debug(f"Fetching JWKS keys from: {settings.KEYS_URL}")
        try:
            response = requests.get(settings.KEYS_URL, timeout=30)  # Add timeout for safety
            response.raise_for_status()
            all_keys = response.json().get('keys')

            if not all_keys:
                logger.error("JWKS endpoint returned no keys")
                raise Exception("Failed to fetch keys")

            # Cache each key individually by kid
            cache_timeout = getattr(settings, 'JWK_CACHE_TIMEOUT', 60 * 60)  # 1 hour cache
            for key in all_keys:
                kid = key["kid"]
                caches['default'].set(f'jwk_{kid}', key, timeout=cache_timeout)
                logger.debug(f"Cached JWKS key: {kid}")

            logger.info(f"Successfully cached {len(all_keys)} JWKS keys")

        except requests.RequestException as e:
            logger.error(f"Failed to fetch JWKS keys: {str(e)}", exc_info=True)
            raise Exception(f"Failed to fetch keys: {str(e)}")

    @staticmethod
    def get_jwk(kid: str) -> dict:
        """
        Retrieve a JSON Web Key (JWK) by its key ID from cache or fetch if not available.

        Args:
            kid: The key ID to retrieve

        Returns:
            dict: The JWK data structure, or None if not found
        """
        logger.debug(f"Retrieving JWK for kid: {kid}")

        # Try to get key from cache first
        if key := caches['default'].get(f'jwk_{kid}', None):
            logger.debug(f"Found cached JWK for kid: {kid}")
            return key

        # If not in cache, refresh all keys and try again
        logger.debug(f"JWK not in cache, refreshing keys for kid: {kid}")
        VerifyTokenMiddleware.cache_jwks_keys()

        key = caches['default'].get(f'jwk_{kid}', None)
        if key:
            logger.debug(f"Found JWK after refresh for kid: {kid}")
        else:
            logger.warning(f"JWK not found even after refresh for kid: {kid}")

        return key

    @staticmethod
    def decode_token(token: str, audience: Union[str, None] = None) -> dict:
        """
        Decode and verify a JWT token using JWKS public keys.

        This method:
        1. Extracts the key ID from the token header
        2. Retrieves the corresponding public key from cache/JWKS endpoint
        3. Verifies the token signature and claims
        4. Returns the decoded payload

        Args:
            token: The JWT token to decode
            audience: Optional audience claim to verify (used for ID tokens)

        Returns:
            dict: The decoded token payload

        Raises:
            jwt.InvalidTokenError: If token verification fails
            Exception: If unable to retrieve the public key
        """
        logger.debug("Starting JWT token decode process")

        # Extract key ID from token header
        header = jwt.get_unverified_header(token)
        kid = header.get('kid')

        if not kid:
            logger.error("Token header missing 'kid' field")
            raise jwt.InvalidTokenError("Token header missing key ID")

        logger.debug(f"Token uses key ID: {kid}")

        # Get the public key for verification
        jwk_value = VerifyTokenMiddleware.get_jwk(kid)
        if not jwk_value:
            logger.error(f"Unable to retrieve JWK for kid: {kid}")
            raise Exception(f"Unable to retrieve public key for kid: {kid}")

        # Convert JWK to public key object
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk_value))

        # Decode and verify the token
        logger.debug(f"Decoding token with audience: {audience}")
        decoded_payload = jwt.decode(token, public_key, audience=audience, algorithms=['RS256'])

        logger.debug("JWT token successfully decoded and verified")
        return decoded_payload

    # Error response methods with logging
    @staticmethod
    def invalid_audience_response():
        """Return JSON response for invalid audience error."""
        logger.warning("Returning invalid audience response")
        return JsonResponse(
            data={'detail': 'Invalid audience'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def token_expire_response():
        """Return JSON response for expired token error."""
        logger.warning("Returning token expired response")
        return JsonResponse(
            data={'message': 'Token expired', 'code': 'Token expired'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def invalid_padding_response():
        """Return JSON response for invalid padding error."""
        logger.warning("Returning invalid padding response")
        return JsonResponse(
            data={'detail': 'Invalid payload padding'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def invalid_crypto_padding_response():
        """Return JSON response for invalid crypto padding error."""
        logger.warning("Returning invalid crypto padding response")
        return JsonResponse(
            data={'detail': 'Invalid crypto padding'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def invalid_token_response():
        """Return JSON response for invalid token error."""
        logger.warning("Returning invalid token response")
        return JsonResponse(
            data={'detail': 'Invalid token'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def no_keys_response():
        """Return JSON response when JWKS endpoint has no keys."""
        logger.warning("Returning no keys response")
        return JsonResponse(
            data={'details': 'The JWKS endpoint does not contain any keys'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def access_token_is_missing_response():
        """Return JSON response for missing access token."""
        logger.warning("Returning access token missing response")
        return JsonResponse(
            data={'detail': 'Access token missing'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def id_token_is_missing_response():
        """Return JSON response for missing ID token."""
        logger.warning("Returning ID token missing response")
        return JsonResponse(
            data={'details': 'Id token missing'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def tokens_are_missing_response():
        """Return JSON response for missing both tokens."""
        logger.warning("Returning both tokens missing response")
        return JsonResponse(
            data={'details': 'Access and id tokens are missing'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def not_enough_segments():
        """Return JSON response for malformed token (not enough segments)."""
        logger.warning("Returning not enough segments response")
        return JsonResponse(
            data={'detail': 'Not enough segments'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    @staticmethod
    def failed_verify_response():
        """Return JSON response for general verification failure."""
        logger.warning("Returning failed verification response")
        return JsonResponse(
            data={'detail': 'Failed to verify token'},
            status=status.HTTP_401_UNAUTHORIZED,
        )
