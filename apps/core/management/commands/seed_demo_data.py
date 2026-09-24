from django.core.management.base import BaseCommand

from apps.catalog.models import Brand, Category, Product
from apps.core.models import SiteSetting


class Command(BaseCommand):
    help = "Seeds minimal demo data (site settings, categories, products) for local development."

    def handle(self, *args, **options):
        settings_obj, _ = SiteSetting.objects.get_or_create(pk=1)
        settings_obj.site_name = "داروخانه آرمان"
        settings_obj.tagline = "سلامت شما، اولویت ماست"
        settings_obj.default_meta_description = "خرید آنلاین دارو، مکمل و لوازم بهداشتی با مشاوره داروساز و ارسال سریع."
        settings_obj.phone_number = "021-12345678"
        settings_obj.email = "info@arman-pharmacy.example"
        settings_obj.address = "تهران، خیابان ولیعصر"
        settings_obj.save()

        categories = [
            ("داروهای بدون نسخه", False),
            ("مکمل‌های ورزشی", False),
            ("لوازم آرایشی و بهداشتی", False),
            ("داروهای نیازمند نسخه", True),
        ]
        category_objs = []
        for name, _rx in categories:
            category, _ = Category.objects.get_or_create(name=name)
            category_objs.append((category, _rx))

        brand, _ = Brand.objects.get_or_create(name="آرمان فارما")

        sample_products = [
            ("قرص ویتامین D3 1000 واحد", 185000, False),
            ("پودر پروتئین وی", 950000, False),
            ("ژل ضدآفتاب SPF50", 320000, False),
            ("قطره آهن کودکان", 210000, False),
            ("آموکسی‌سیلین 500 میلی‌گرم", 95000, True),
        ]
        for i, (name, price, requires_rx) in enumerate(sample_products):
            category = category_objs[3][0] if requires_rx else category_objs[i % 3][0]
            Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "brand": brand,
                    "price": price,
                    "stock": 50,
                    "sku": f"SKU-{1000 + i}",
                    "requires_prescription": requires_rx,
                    "is_featured": i < 3,
                    "short_description": f"{name} با کیفیت تضمین‌شده و اصالت کامل.",
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
