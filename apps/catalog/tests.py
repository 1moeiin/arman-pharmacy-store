import pytest

from apps.catalog.models import Category, Product


@pytest.mark.django_db
class TestProduct:
    def _make_category(self):
        return Category.objects.create(name="داروهای بدون نسخه")

    def test_slug_auto_generated_from_persian_name(self):
        category = self._make_category()
        product = Product.objects.create(
            name="قرص ویتامین D3",
            category=category,
            price=100000,
            sku="SKU-1",
        )
        assert product.slug
        assert " " not in product.slug

    def test_price_in_rials_is_ten_times_toman_price(self):
        category = self._make_category()
        product = Product.objects.create(
            name="محصول تست", category=category, price=1000, sku="SKU-2",
        )
        assert product.price_in_rials == 10000

    def test_discount_percent(self):
        category = self._make_category()
        product = Product.objects.create(
            name="محصول تست", category=category, price=800, compare_at_price=1000, sku="SKU-3",
        )
        assert product.discount_percent == 20

    def test_in_stock(self):
        category = self._make_category()
        product = Product.objects.create(
            name="محصول تست", category=category, price=1000, stock=0, sku="SKU-4",
        )
        assert product.in_stock is False
