# account_levels/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class AccountType(models.Model):
    """
    Defines the different account levels available in the system.
    Developers will configure these via fixtures or admin.
    """
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Free, Premium, Gold")
    level = models.IntegerField(
        unique=True,
        validators=[MinValueValidator(0)],
        help_text="Numerical hierarchy (0 for Free, 1 for Premium, etc.). Higher number = higher level."
    )
    description = models.TextField(blank=True, help_text="Optional description of this account type.")

    class Meta:
        ordering = ['level']
        verbose_name = "Account Type"
        verbose_name_plural = "Account Types"

    def __str__(self):
        return f"{self.name} (Level: {self.level})"

class UserAccountLevel(models.Model):
    """
    Links a Django User to their current AccountType.
    This is the dedicated model for tracking user account levels.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_level')
    
    # ForeignKey to AccountType, allowing null initially for post_migrate sync
    account_type = models.ForeignKey(
        AccountType,
        on_delete=models.SET_NULL, # If an AccountType is deleted, users default to null (or default_account_type)
        null=True,
        blank=True,
        related_name='users'
    )
    
    # You could add other fields here, like 'upgrade_date', 'expiry_date' etc.

    class Meta:
        verbose_name = "User Account Level"
        verbose_name_plural = "User Account Levels"

    def get_level_numeric(self):
        """Returns the numerical level of the user's current account type."""
        if self.account_type:
            return self.account_type.level
        # Fallback to 0 if account_type is null (e.g., if default not set yet)
        return 0 

    def __str__(self):
        level_name = self.account_type.name if self.account_type else "No Account Type"
        return f"{self.user.username}'s Account: {level_name}"
