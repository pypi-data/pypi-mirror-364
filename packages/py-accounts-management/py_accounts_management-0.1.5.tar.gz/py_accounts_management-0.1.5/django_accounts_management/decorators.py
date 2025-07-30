# account_levels/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.apps import apps # To safely get models if needed, though direct relation is better
from .models import UserAccountLevel, AccountType
from .exceptions import AccountLevelsConfigurationError

def account_level_required(minimum_level_name, redirect_url=None):
    """
    Decorator to restrict access to views based on user's AccountType level.

    Args:
        minimum_level_name (str): The name of the AccountType (e.g., 'Premium', 'Gold')
                                  required to access the decorated view.
                                  This name must exist in your AccountType model.

        redirect_url (str, optional): The URL name or path to redirect to if the user
                                      does not meet the required level.
                                      If not provided, it defaults to a URL specified
                                      in settings.ACCOUNT_LEVELS_UPGRADE_URL_NAME
                                      or a generic 'home'.

    Raises:
        AccountLevelsConfigurationError: If the minimum_level_name does not exist
                                         as an AccountType in the database,
                                         or if redirect_url is not configured.
        RuntimeError: If the provided redirect_url cannot be resolved.
    """
    # Pre-fetch the required AccountType level once when the decorator is defined
    # This catches configuration errors early.
    _required_account_type_obj = None
    _required_level_numeric = -1 # Default to -1 so any valid level (>=0) is higher

    # We need to defer model access until Django's app registry is ready.
    # This block runs when the decorator is first imported.
    # It's generally safer to do model lookups in `ready()` or within the view.
    # For a decorator, we capture the name and look it up at runtime.

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 1. Check if the user is authenticated
            if not request.user.is_authenticated:
                messages.info(request, "You need to log in to access this page.")
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            # 2. Get the user's dedicated UserAccountLevel instance
            try:
                # Access via the related_name 'account_level'
                user_account_level_instance = request.user.account_level
                user_current_level_numeric = user_account_level_instance.get_level_numeric()
            except UserAccountLevel.DoesNotExist:
                # This should ideally be prevented by the post_save/post_migrate signals,
                # but handle it robustly.
                messages.error(request, "Your account level profile is missing. Please contact support.")
                # Redirect to logout or a page to fix profile
                return redirect(reverse(getattr(settings, 'ACCOUNT_LEVELS_PROFILE_MISSING_REDIRECT_URL', 'home')))
            
            # 3. Get the numerical level for the required minimum_level_name
            # This lookup happens per request, ensuring the AccountType model is ready.
            AccountType = apps.get_model('django_accounts_management', 'AccountType')
            try:
                required_account_type_obj = AccountType.objects.get(name__iexact=minimum_level_name)
                required_level_numeric = required_account_type_obj.level #type: ignore
            except AccountType.DoesNotExist:
                raise AccountLevelsConfigurationError(
                    f"The required minimum_level_name '{minimum_level_name}' "
                    f"does not exist in your AccountType model. "
                    f"Please define it in the Django admin or via a data migration."
                )

            # 4. Compare the user's level with the required minimum level
            if user_current_level_numeric < required_level_numeric:
                messages.warning(
                    request,
                    f"Your current account is not sufficient for this feature. "
                    f"Please upgrade to at least {minimum_level_name.capitalize()}."
                )

                # Determine the redirect URL
                final_redirect_path = None
                target_redirect_url = redirect_url or getattr(settings, 'ACCOUNT_LEVELS_UPGRADE_URL_NAME', None)

                if not target_redirect_url:
                    # If no redirect_url is provided to decorator AND no default in settings
                    raise AccountLevelsConfigurationError(
                        f"No redirect_url specified for @account_level_required on '{view_func.__name__}', "
                        f"and ACCOUNT_LEVELS_UPGRADE_URL_NAME is not set in settings.py. "
                        f"Please define one or both."
                    )

                try:
                    # Attempt to reverse the URL name or use as direct path
                    final_redirect_path = reverse(target_redirect_url)
                except NoReverseMatch:
                    # If it's not a URL name, assume it's a direct path
                    final_redirect_path = target_redirect_url
                except Exception as e:
                    raise RuntimeError(
                        f"Unexpected error resolving redirect_url '{target_redirect_url}' for '{view_func.__name__}': {e}"
                    )

                if not final_redirect_path:
                    raise RuntimeError(
                        f"Critical Configuration Error for @account_level_required on '{view_func.__name__}': "
                        f"The redirect_url '{target_redirect_url}' resulted in an empty path. "
                        f"This should not happen with proper validation. Check your `redirect_url`."
                    )
                
                # Pass the 'next' parameter to the upgrade URL
                return redirect(f"{final_redirect_path}?next={request.path}")

            # 5. If the user has the required level, proceed to the original function
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator



'''


def group_required(group_names, redirect_url):
    """
    Decorator to restrict access to views based on user group membership.

    Args:
        group_names (str or list/tuple of str):
            A single group name string, or a list/tuple of group names.
            The user must be a member of AT LEAST ONE of these groups to access the view.

        redirect_url (str):
            The URL name (e.g., 'home', 'login') or a direct URL path (e.g., '/access-denied/')
            to redirect to if the user does not meet the group requirements.
            This argument is MANDATORY and must always be provided and resolvable.

    Raises:
        TypeError: If `group_names` is not a string or list/tuple of strings.
        ValueError: If `redirect_url` is not a non-empty string.
        RuntimeError: If the provided `redirect_url` cannot be resolved to a valid path
                      during the request, indicating a configuration error.

    Usage:
        @group_required('staff', redirect_url='staff_restricted_access')
        def staff_only_view(request):
            # ...
    """
    if isinstance(group_names, str):
        group_names = [group_names]
    elif not isinstance(group_names, (list, tuple)):
        raise TypeError("group_names must be a string or a list/tuple of strings.")

    if not isinstance(redirect_url, str) or not redirect_url.strip():
        raise ValueError("redirect_url must be a non-empty string representing a URL name or path.")

    # Pre-emptively try to resolve the redirect_url once when the decorator is defined
    # This catches many errors early, at server startup, rather than at request time.
    # However, if the URL depends on dynamic values (e.g., specific object IDs),
    # it might still need to be resolved at request time.
    # For a purely static redirect_url, this is highly beneficial.
    try:
        # We attempt to reverse it here, if it's a URL name.
        # If it's a direct path, reverse() will raise NoReverseMatch, which is fine,
        # it just means it's not a named URL.
        _ = reverse(redirect_url)
        _is_named_url = True
    except NoReverseMatch:
        # It's not a named URL, so it must be a direct path.
        # We can't fully validate a direct path until request time,
        # but we can ensure it's not empty/malformed.
        if not redirect_url.startswith('/'): # Minimal check for a path
            # raise ValueError(f"redirect_url '{redirect_url}' must be a valid URL name or start with '/' for a path.")
            # Let the runtime check handle more nuanced path issues for now.
            pass
        _is_named_url = False # It's a direct path

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, "You need to log in to access this page.")
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            if not request.user.groups.filter(name__in=group_names).exists():
                messages.warning(
                    request,
                    f"You do not have the necessary permissions to access this page. "
                    f"Required groups: {', '.join(group_names)}."
                )

                final_redirect_path = None
                try:
                    if _is_named_url:
                        # If we determined it's a named URL during decorator definition, try reversing it again.
                        final_redirect_path = reverse(redirect_url)
                    else:
                        # Otherwise, it must be a direct path.
                        final_redirect_path = redirect_url
                except NoReverseMatch:
                    # This means it was a named URL, but it couldn't be resolved at runtime (e.g., context missing).
                    # Or, less likely, if _is_named_url logic was complex and failed later.
                    raise RuntimeError(
                        f"Configuration Error for @group_required on '{view_func.__name__}': "
                        f"The redirect_url '{redirect_url}' could not be resolved. "
                        f"Please ensure it is a valid URL name defined in your urls.py "
                        f"or a correctly formatted absolute path (e.g., '/your-path/')."
                    )
                except Exception as e: # Catch any other unexpected issues during resolution
                     raise RuntimeError(
                        f"Unexpected error resolving redirect_url '{redirect_url}' for '{view_func.__name__}': {e}"
                    )

                # This `if not final_redirect_path:` check might become redundant
                # if `reverse` or the initial checks always ensure a valid string.
                # However, as a final safeguard against an empty string being passed
                # from an edge case in the `redirect_url` itself (though unlikely with `strip()` and `isinstance`),
                # we keep a very strict check.
                if not final_redirect_path:
                    # This indicates a very fundamental problem with `redirect_url`'s value
                    # that even initial checks or `NoReverseMatch` didn't catch,
                    # e.g., if it became an empty string somehow.
                    raise RuntimeError(
                        f"Critical Configuration Error for @group_required on '{view_func.__name__}': "
                        f"The redirect_url '{redirect_url}' resulted in an empty path. "
                        f"This should not happen with proper validation. Check your `redirect_url`."
                    )

                return redirect(final_redirect_path)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

    '''




# --- FIX APPLIED TO group_required DECORATOR ---
def group_required(group_names, redirect_url):
    """
    Decorator to restrict access to views based on user group membership.

    Args:
        group_names (str or list/tuple of str):
            A single group name string, or a list/tuple of group names.
            The user must be a member of AT LEAST ONE of these groups to access the view.

        redirect_url (str):
            The URL name (e.g., 'home', 'login') or a direct URL path (e.g., '/access-denied/')
            to redirect to if the user does not meet the group requirements.
            This argument is MANDATORY and must always be provided and resolvable.

    Raises:
        TypeError: If `group_names` is not a string or list/tuple of strings.
        ValueError: If `redirect_url` is not a non-empty string.
        RuntimeError: If the provided `redirect_url` cannot be resolved to a valid path
                      during the request, indicating a configuration error.

    Usage:
        @group_required('staff', redirect_url='staff_restricted_access')
        def staff_only_view(request):
            # ...
    """
    if isinstance(group_names, str):
        group_names = [group_names]
    elif not isinstance(group_names, (list, tuple)):
        raise TypeError("group_names must be a string or a list/tuple of strings.")

    if not isinstance(redirect_url, str) or not redirect_url.strip():
        raise ValueError("redirect_url must be a non-empty string representing a URL name or path.")

    # --- REMOVED THE PROBLEMATIC PRE-EMPTIVE REVERSE() CALL HERE ---
    # The _is_named_url logic is now handled entirely within _wrapped_view.

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.info(request, "You need to log in to access this page.")
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            if not request.user.groups.filter(name__in=group_names).exists():
                messages.warning(
                    request,
                    f"You do not have the necessary permissions to access this page. "
                    f"Required groups: {', '.join(group_names)}."
                )

                final_redirect_path = None
                try:
                    # --- MOVED REVERSE() RESOLUTION TO HERE (RUNTIME) ---
                    final_redirect_path = reverse(redirect_url)
                except NoReverseMatch:
                    # If it's not a named URL, assume it's a direct path
                    final_redirect_path = redirect_url
                except Exception as e:
                    raise RuntimeError(
                        f"Unexpected error resolving redirect_url '{redirect_url}' for '{view_func.__name__}': {e}"
                    )

                if not final_redirect_path:
                    raise RuntimeError(
                        f"Critical Configuration Error for @group_required on '{view_func.__name__}': "
                        f"The redirect_url '{redirect_url}' resulted in an empty path. "
                        f"This should not happen with proper validation. Check your `redirect_url`."
                    )

                return redirect(final_redirect_path)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator