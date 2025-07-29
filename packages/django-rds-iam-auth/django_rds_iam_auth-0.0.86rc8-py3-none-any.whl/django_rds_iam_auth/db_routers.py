import logging
from django.conf import settings
from django_rds_iam_auth.middleware.jwt_exposer import local

# Configure logger for this module
logger = logging.getLogger(__name__)


class GenericRLSSecuredRouter:
    """
    Django database router that controls database connection routing based on Row-Level Security (RLS).

    This router directs database operations to either:
    1. Default connection pool for excluded apps or non-authenticated requests
    2. RLS-secured connection pool for authenticated users with specific database instances

    The RLS secured pool stores connections in REDIS cache (the rls_iam_auth package generates
    the cache for any new instance using cognito service, the TTL is taken from cognito token
    expiration dateTime).

    Important Notes:
    - This router is for operational work only and will NOT be used for running migrations
    - The responsibility for migrations resides with the host application
    - Excluded apps (defined in settings.EXCLUDE_APP_FROM_SECURE_RLS) always use default connection

    Attributes:
        excluded_apps: List of Django app labels that should use default database connection
    """

    # Apps that should always use the default database connection
    excluded_apps = settings.EXCLUDE_APP_FROM_SECURE_RLS

    def __init__(self):
        """Initialize the router and log configuration."""
        logger.info(f"GenericRLSSecuredRouter initialized with excluded apps: {self.excluded_apps}")

    @staticmethod
    def has_method(o, name):
        """
        Check if an object has a callable method with the given name.

        Args:
            o: The object to check
            name: The method name to look for

        Returns:
            bool: True if the object has the callable method, False otherwise
        """
        return callable(getattr(o, name, None))

    def db_for_read(self, model, **hints):
        """
        Determine which database to use for read operations.

        If the model's app is not in the excluded apps list and we have an authenticated
        user with a valid user_id in thread-local storage, use the RLS secured connection.
        Otherwise, use the default database connection.

        Args:
            model: The Django model class for which to determine the database
            **hints: Additional hints that might influence database selection

        Returns:
            str or None: Database alias to use for reads, or None to use default routing
        """
        app_label = model._meta.app_label
        user_id = getattr(local, 'user_id', None)

        # Check if app should use RLS secured connection
        if app_label not in self.excluded_apps and user_id is not None:
            logger.debug(f"Routing read operation for {app_label}.{model.__name__} to RLS database: {user_id}")
            return user_id

        logger.debug(f"Routing read operation for {app_label}.{model.__name__} to default database")
        return None

    def db_for_write(self, model, **hints):
        """
        Determine which database to use for write operations.

        If the model's app is not in the excluded apps list and we have an authenticated
        user with a valid user_id in thread-local storage, use the RLS secured connection.
        Otherwise, use the default database connection.

        Args:
            model: The Django model class for which to determine the database
            **hints: Additional hints that might influence database selection

        Returns:
            str or None: Database alias to use for writes, or None to use default routing
        """
        app_label = model._meta.app_label
        user_id = getattr(local, 'user_id', None)

        # Check if app should use RLS secured connection
        if app_label not in self.excluded_apps and user_id is not None:
            logger.debug(f"Routing write operation for {app_label}.{model.__name__} to RLS database: {user_id}")
            return user_id

        logger.debug(f"Routing write operation for {app_label}.{model.__name__} to default database")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Determine if a relation between two objects should be allowed.

        For this router, we allow all relations as the responsibility for
        managing relations lies with the host application.

        Args:
            obj1: First model instance in the relation
            obj2: Second model instance in the relation
            **hints: Additional hints that might influence the decision

        Returns:
            bool: True to allow the relation, False to deny it, None for no opinion
        """
        logger.debug(f"Allowing relation between {type(obj1).__name__} and {type(obj2).__name__}")
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Determine if a migration should be allowed to run on a specific database.

        Migration responsibility lies with the host application, so this router
        does not provide any opinion on migration routing.

        Args:
            db: Database alias where the migration would run
            app_label: Django app label for the migration
            model_name: Model name for the migration (if applicable)
            **hints: Additional hints that might influence the decision

        Returns:
            None: No opinion on migration routing (defers to other routers or defaults)
        """
        logger.debug(f"Migration check for app '{app_label}' on database '{db}' - deferring to host app")
        return None
