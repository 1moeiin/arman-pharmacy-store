import pytest
from django.db import IntegrityError

from apps.accounts.models import User


@pytest.mark.django_db
class TestUserManager:
    def test_create_user_with_phone_number(self):
        user = User.objects.create_user(phone_number="09121234567", password="StrongPass123")
        assert user.phone_number == "09121234567"
        assert user.check_password("StrongPass123")
        assert not user.is_staff

    def test_duplicate_phone_number_rejected_at_db_level(self):
        User.objects.create_user(phone_number="09121234567", password="StrongPass123")
        with pytest.raises(IntegrityError):
            User.objects.create_user(phone_number="09121234567", password="AnotherPass123")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(phone_number="09129999999", password="AdminPass123")
        assert admin.is_staff
        assert admin.is_superuser
