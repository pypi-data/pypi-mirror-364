import logging
import datetime
import dns.resolver
import dns.rdatatype
from dns.exception import DNSException

import boto3
from django.conf import settings
from django.db import connections
from django.utils.connection import ConnectionProxy

# Configure logger for this module
logger = logging.getLogger(__name__)


def is_connection_valid(alias: str, raise_exception: bool = False) -> bool:
    """
    Test if a database connection is valid by attempting to create a cursor.

    This function checks if a database connection identified by the given alias
    is functional by trying to obtain a cursor from it. This is a lightweight
    way to verify connection health without executing actual queries.

    Args:
        alias: Database connection alias to test
        raise_exception: If True, re-raise the exception instead of returning False

    Returns:
        bool: True if connection is valid and functional, False otherwise

    Raises:
        Exception: If raise_exception is True and connection test fails
    """
    logger.debug(f"Testing connection validity for alias: {alias}")

    try:
        # Attempt to create a cursor - this will fail if connection is invalid
        cursor = ConnectionProxy(connections, alias).cursor()
        cursor.close()  # Clean up the cursor
        logger.debug(f"Connection {alias} is valid")
        return True

    except Exception as e:
        logger.warning(f"Connection {alias} is invalid: {str(e)}")
        if raise_exception:
            logger.error(f"Re-raising connection exception for {alias}")
            raise e
        return False


def create_connection(default_connection: dict, alias: str, credentials: dict) -> dict:
    """
    Create a new database connection configuration with IAM authentication.

    This function takes a default database connection configuration and modifies
    it to use AWS IAM authentication with the provided credentials. It generates
    an authentication token using the RDS client and configures the connection
    for the specified user alias.

    Args:
        default_connection: Base database connection configuration dictionary
        alias: User alias to use as both connection ID and database username
        credentials: AWS credentials dictionary containing access keys and tokens

    Returns:
        dict: Modified database connection configuration with IAM auth

    Raises:
        Exception: If unable to generate authentication token or create boto3 session
    """
    logger.info(f"Creating dynamic database connection for alias: {alias}")

    try:
        # Create a new boto3 session with the provided credentials
        logger.debug(f"Creating boto3 session for alias: {alias}")
        boto3_session = boto3.session.Session(**credentials)

        # Create RDS client for generating authentication tokens
        rds_client = boto3_session.client("rds")

        # Configure the connection parameters
        connection_config = default_connection.copy()
        connection_config['id'] = alias
        connection_config['USER'] = alias
        engine = getattr(settings, 'DYNAMIC_CONNECTION_ENGINE', 'django_rds_iam_auth.aws.postgresql')
        connection_config['ENGINE'] = engine

        # Set connection max age from settings with fallback
        max_age = getattr(settings, 'DYNAMIC_CONNECTION_MAX_AGE', 2 * 60)  # Default to 2 minutes
        connection_config['CONN_MAX_AGE'] = max_age
        logger.debug(f"Set connection max age to: {max_age} seconds")

        # Generate IAM database authentication token
        db_host = connection_config['HOST']
        db_port = connection_config.get('PORT', 5432)

        logger.debug(f"Generating auth token for {alias}@{db_host}:{db_port}")
        auth_token = rds_client.generate_db_auth_token(
            DBHostname=db_host,
            Port=db_port,
            DBUsername=alias,
        )

        connection_config['PASSWORD'] = auth_token
        logger.info(f"Successfully created connection configuration for alias: {alias}")

        return connection_config

    except Exception as e:
        logger.error(f"Failed to create connection for alias {alias}: {str(e)}", exc_info=True)
        raise Exception(f"Unable to create database connection: {str(e)}")


def resolve_cname(hostname):
    """Resolve a CNAME record to the original hostname.

    This is required for AWS where the hostname of the RDS instance is part of
    the signing request.

    """
    try:
        answers = dns.resolver.query(hostname, "CNAME")
        for answer in answers:
            if answer.rdtype == dns.rdatatype.CNAME:
                return answer.to_text().strip('.')
    except DNSException:
        return hostname


def set_cookie(response, domain, key, value, days_expire=7, secure=None):
  if days_expire is None:
    max_age = 365 * 24 * 60 * 60  #one year
  else:
    max_age = days_expire * 24 * 60 * 60
  expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
  response.set_cookie(key, value, max_age=max_age, expires=expires, domain=domain, secure=secure or None)
