from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود.",
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("شماره موبایل الزامی است.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("ابرکاربر باید is_staff=True داشته باشد.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("ابرکاربر باید is_superuser=True داشته باشد.")
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    """Phone-number-based user. `username` is kept (unused) so third-party
    code expecting AbstractUser's default field keeps working, but auth
    happens via phone_number."""

    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    phone_number = models.CharField(
        max_length=11, unique=True, validators=[phone_validator], verbose_name="شماره موبایل"
    )
    email = models.EmailField(blank=True)
    national_id = models.CharField(max_length=10, blank=True, verbose_name="کد ملی")
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def __str__(self):
        return self.get_full_name() or self.phone_number


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=60, help_text="مثلاً: خانه، محل کار")
    receiver_full_name = models.CharField(max_length=150)
    receiver_phone_number = models.CharField(max_length=11, validators=[phone_validator])
    province = models.CharField(max_length=60)
    city = models.CharField(max_length=60)
    postal_code = models.CharField(max_length=10)
    full_address = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.receiver_full_name}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
