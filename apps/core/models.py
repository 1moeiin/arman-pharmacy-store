from django.core.cache import cache
from django.db import models


class SiteSetting(models.Model):
    """Singleton row holding editable, site-wide SEO/content settings."""

    site_name = models.CharField(max_length=120, default="داروخانه آرمان")
    tagline = models.CharField(max_length=200, blank=True)
    default_meta_description = models.CharField(max_length=320, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    instagram_url = models.URLField(blank=True)
    whatsapp_url = models.URLField(blank=True)
    og_image = models.ImageField(upload_to="site/", blank=True, null=True)
    google_site_verification = models.CharField(max_length=120, blank=True)

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    @classmethod
    def load(cls):
        settings_obj = cache.get("site_settings")
        if settings_obj is None:
            settings_obj, _ = cls.objects.get_or_create(pk=1)
            cache.set("site_settings", settings_obj, 60 * 60)
        return settings_obj


class ContactMessage(models.Model):
    """Messages submitted through the public contact form."""

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_handled = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "پیام تماس"
        verbose_name_plural = "پیام‌های تماس"

    def __str__(self):
        return f"{self.name} <{self.email}>"
