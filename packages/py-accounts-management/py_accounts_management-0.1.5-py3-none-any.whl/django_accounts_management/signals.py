# account_levels/signals.py
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.apps import apps # To safely get models during post_migrate
from django.conf import settings
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_account_level(sender, instance, created, **kwargs):
    """
    Signal to create a UserAccountLevel instance automatically when a new User is created.
    Assigns the default account type if configured.
    """
    if created:
        UserAccountLevel = apps.get_model('django_accounts_management', 'UserAccountLevel')
        AccountType = apps.get_model('django_accounts_management', 'AccountType')

        default_account_type_name = getattr(settings, 'ACCOUNT_LEVELS_DEFAULT_TYPE', None)
        default_account_type = None

        if default_account_type_name:
            try:
                default_account_type = AccountType.objects.get(name=default_account_type_name)
            except AccountType.DoesNotExist:
                # Log this error, but don't prevent user creation
                print(f"WARNING: Default AccountType '{default_account_type_name}' not found. New user '{instance.username}' will have no initial account type.")
        
        UserAccountLevel.objects.create(user=instance, account_type=default_account_type)

@receiver(post_save, sender=User)
def save_user_account_level(sender, instance, **kwargs):
    """
    Signal to save the UserAccountLevel whenever the User object is saved.
    Ensures the profile stays in sync if the user object itself is manipulated.
    """
    if hasattr(instance, 'account_level'): # Check if it exists to prevent errors during initial creation
        instance.account_level.save()


@receiver(post_migrate)
def sync_existing_users_with_account_levels(sender, app_config, **kwargs):
    """
    Signal to ensure all existing users have a UserAccountLevel instance
    after migrations for this app are applied.
    Assigns the default account type configured in settings.
    """
    if app_config.name == 'account_levels': # Ensure this runs only for YOUR app's migrations
        User = apps.get_model('auth', 'User')
        UserAccountLevel = apps.get_model('account_levels', 'UserAccountLevel')
        AccountType = apps.get_model('account_levels', 'AccountType')

        default_account_type_name = getattr(settings, 'ACCOUNT_LEVELS_DEFAULT_TYPE', None)
        default_account_type = None

        if default_account_type_name:
            try:
                default_account_type = AccountType.objects.get(name=default_account_type_name)
            except AccountType.DoesNotExist:
                print(f"WARNING: Default AccountType '{default_account_type_name}' not found during post_migrate. Existing users will have no initial account type.")
        
        # Find users without an associated UserAccountLevel
        users_without_level = User.objects.filter(account_level__isnull=True)
        
        if kwargs.get('verbosity', 0) >= 1: # Print messages if verbosity is high enough
            print(f"Syncing {users_without_level.count()} existing users with UserAccountLevel...")

        for user in users_without_level:
            UserAccountLevel.objects.create(user=user, account_type=default_account_type)
            if kwargs.get('verbosity', 0) >= 1:
                print(f" - Created UserAccountLevel for user: {user.username}") # Log each creation for clarity