# account_levels/admin.py
from django.contrib import admin
from .models import AccountType, UserAccountLevel

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'description')
    search_fields = ('name',)
    ordering = ('level',)

@admin.register(UserAccountLevel)
class UserAccountLevelAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'get_level_numeric')
    list_filter = ('account_type',)
    search_fields = ('user__username', 'account_type__name')
    raw_id_fields = ('user',) # Useful for many users
