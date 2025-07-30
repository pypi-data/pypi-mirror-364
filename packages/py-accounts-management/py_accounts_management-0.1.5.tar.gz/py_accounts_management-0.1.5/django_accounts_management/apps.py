

'''class DjangoAccountsManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_accounts_management'
'''


# account_levels/apps.py
from django.apps import AppConfig
from django.conf import settings
from .exceptions import AccountLevelsConfigurationError 
# Your custom exception


class DjangoAccountsManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_accounts_management'
    verbose_name = "Account Levels Management"

    def ready(self):
        """
        This method is called when Django starts up.
        It's the perfect place for:
        1. Validating custom settings.
        2. Connecting signals.
        """
        # 1. Validate custom settings from settings.py
        self.validate_settings()

        # 2. Import and connect signals
        # We import here to avoid circular import issues during Django's startup process
        import django_accounts_management.signals  
        

    def validate_settings(self):
        """
        Ensure all required custom settings for account_levels are present and correctly formatted.
        """
        # Check for ACCOUNT_LEVELS_DEFAULT_TYPE
        default_type = getattr(settings, 'ACCOUNT_LEVELS_DEFAULT_TYPE', None)
        if not default_type:
            raise AccountLevelsConfigurationError(
                "ACCOUNT_LEVELS_DEFAULT_TYPE must be defined in your settings.py "
                "for the django-accounts-management app. This should be the name of your "
                "default (e.g., 'Free') AccountType."
            )
        if not isinstance(default_type, str):
            raise AccountLevelsConfigurationError(
                "ACCOUNT_LEVELS_DEFAULT_TYPE in settings.py must be a string."
            )

        # You can add more validation here, e.g.,
        # - Check if a specific URL for upgrade is set (if your decorator needs it)
        # - Check if AccountType model has any instances (after initial migration)