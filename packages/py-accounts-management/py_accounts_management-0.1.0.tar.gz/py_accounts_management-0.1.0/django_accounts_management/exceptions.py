# account_levels/exceptions.py

from django.core.exceptions import ImproperlyConfigured

class AccountLevelsConfigurationError(ImproperlyConfigured):
    """
    Custom exception for configuration errors related to django-account-levels.
    """
    pass