# Py Accounts Management

![PyPI - Version](https://img.shields.io/pypi/v/django-account-levels.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-accounts-management.svg)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-account-levels.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A reusable Django application for managing flexible user account levels and controlling access to features based on these levels. Easily define custom account types (e.g., Free, Premium, Gold) and integrate level-based access control into your views.

Also categorize the users of those accounts into various groups depending on the number of gates or portals you have in your application and the access algorithm you want,

Manage roles of different users in the same group but with different status or account level,

an account level based view can be acccessed bhy various users of the same account level but in different multiple groups based on your system requirements

---

## Table of Contents

* [Features](#features)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
    * [Defining Account Types](#defining-account-types)
    * [Assigning Account Types to Users](#assigning-account-types-to-users)
    * [Using the Decorators](#using-the-decorator)
    * [Integrating with User Upgrade Form](#integrating-with-user-upgrade-form)
* [Signals](#signals)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* **Flexible Account Types:** Define custom account levels (e.g., 'Free', 'Pro', 'Elite') with numerical hierarchy directly in your Django admin.
* **Dedicated User Account Level Model:** A `UserAccountLevel` model automatically created and linked to each Django `User`, storing their current account type.
* **Automatic User Sync:** Automatically assigns a default account type to new users and syncs existing users upon installation/migration.
* **`@account_level_required` Decorator:** Easily restrict access to views based on a minimum required account level.
* **'@group_required' Decorator:** Easily restricts access from users not in the specified groups if yo are using the django's built-in  group model. It specifies either a name of a single group or the list of group names assosiated with that view.
* **Configurable Redirects:** Customize the redirect URL for unauthorized access directly in your Django `settings.py` or per decorator instance.
* **Clear Error Handling:** Provides informative error messages for developers if configuration is incorrect.

## Installation for django development

1.  **Install the package via pip:**
    ```bash
    pip  install py-accounts-management
    ```

2.  **Add `django-accounts-management` to your `INSTALLED_APPS` in `settings.py`:**
    ```python
    # myproject/settings.py

    INSTALLED_APPS = [
        # ... other Django apps
        'django_accounts_management',
        # ... your project's apps
    ]
    ```

3.  **Run migrations:**
    This will create the necessary database tables for `AccountType` and `UserAccountLevel` models, and automatically assign the default account type to existing users based on your settings.
    ```bash
    python manage.py migrate
    ```

## Configuration

Add the following settings to your `settings.py` file:

```python
# myproject/settings.py

# --- Django Account Levels Settings ---

# The name of the default AccountType for new and existing users upon migration.
# This MUST match the 'name' field of an AccountType instance you create in the admin.
# Example: 'Free'
ACCOUNT_LEVELS_DEFAULT_TYPE = 'Free' 

# The URL name (from your project's urls.py) to redirect users to for upgrading their account.
# This is used by the @account_level_required decorator when a user's level is insufficient.
# Example: 'myapp:upgrade_account' (if your upgrade view is in 'myapp' app with namespace)
ACCOUNT_LEVELS_UPGRADE_URL_NAME = 'upgrade_account' 

# The URL name to redirect users to if their UserAccountLevel profile is missing.
# This is a robust fallback for unexpected data issues.
# Example: 'home' or 'myapp:home'
ACCOUNT_LEVELS_PROFILE_MISSING_REDIRECT_URL = 'home' 

# --- Standard Django Auth Settings (ensure these are also set) ---
LOGIN_URL = '/login/' # Your project's login URL
LOGIN_REDIRECT_URL = '/' # Where to redirect after successful login
LOGOUT_REDIRECT_URL = '/' # Where to redirect after logout

# using the decorator

# import the decorator in your views.py

'''
from django.contrib.auth.decorators import login_required
from django_accounts_management.decorators import account_level_required, group_required

@login_required
@group_required('consumers', redirect_url='EluxProcessor:buy_elux')
@account_level_required('Basic', redirect_url='EluxProcessor:buy_elux')

def test_view(request):
    """
    A simple view to test the setup.
    """
    return HttpResponse("This is a test view to ensure the Django setup is working correctly.")
# Create your views here.


'''

# or the group decolators can be used as the list of groups if you need to set the view appropriate to more than one view

# @group_required(['consumers', 'sme', ], redirect_url='EluxProcessor:buy_elux')

'''

the decorators for the account level and group are independent on each other, can be used separately to match the context of yor demand

'''