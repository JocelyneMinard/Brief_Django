from django.contrib import admin
from django.contrib.auth import get_user_model
from cuser.admin import UserAdmin

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Library Information", {"fields": ("role", "membership_number")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Library Information", {"fields": ("role", "membership_number")}),
    )
    list_display = ("email", "first_name", "last_name", "role", "membership_number", "is_staff")
    list_filter = ("role", "is_staff", "is_active", "groups")