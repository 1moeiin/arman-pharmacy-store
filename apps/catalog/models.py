from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ActiveManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, allow_unicode=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="children")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    icon_class = models.CharField(max_length=60, blank=True, help_text="مثلاً نام آیکون برای نمایش در منو")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    objects = ActiveManager()

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["order", "name"]
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["is_active", "parent"])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:category_detail", kwargs={"slug": self.slug})

    @property
    def seo_title(self):
        return self.meta_title or self.name

    @property
    def seo_description(self):
        return self.meta_description or (self.description[:157] + "…" if len(self.description) > 160 else self.description)


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, allow_unicode=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, blank=True)
    generic_name = models.CharField(max_length=200, blank=True, help_text="نام ژنریک/علمی برای جستجوی بهتر")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True, verbose_name="نحوه مصرف")
    side_effects = models.TextField(blank=True, verbose_name="عوارض جانبی")

    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    compare_at_price = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True,
        help_text="قیمت قبل از تخفیف (اختیاری)",
    )
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=64, unique=True)

    requires_prescription = models.BooleanField(default=False, verbose_name="نیازمند نسخه پزشک")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveManager()

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "category"]),
            models.Index(fields=["is_active", "is_featured"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def price_in_rials(self):
        """Prices are stored/displayed in Toman; schema.org structured data
        needs the ISO 4217 code IRR (Rial), which is 10x the Toman value."""
        return self.price * 10

    @property
    def discount_percent(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round((1 - (self.price / self.compare_at_price)) * 100)
        return 0

    @property
    def seo_title(self):
        return self.meta_title or self.name

    @property
    def seo_description(self):
        if self.meta_description:
            return self.meta_description
        text = self.short_description or self.description
        return text[:157] + "…" if len(text) > 160 else text

    @property
    def primary_image(self):
        return self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=160, blank=True, help_text="متن جایگزین برای سئو و دسترس‌پذیری")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ["order", "id"]

    def __str__(self):
        return self.alt_text or f"{self.product.name} — {self.order}"

    def display_alt(self):
        return self.alt_text or self.product.name
