from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = ["phone_number", "first_name", "last_name", "is_phone_verified", "is_staff"]
    search_fields = ["phone_number", "first_name", "last_name", "email"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("اطلاعات شخصی", {"fields": ("first_name", "last_name", "email", "national_id")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_phone_verified", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone_number", "password1", "password2")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "city", "is_default"]
    search_fields = ["user__phone_number", "city", "full_address"]
    list_filter = ["province", "is_default"]
