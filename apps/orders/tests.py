import pytest

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.orders.models import Order


@pytest.fixture
def category(db):
    return Category.objects.create(name="داروهای بدون نسخه")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="قرص ویتامین D3", category=category, price=100000, stock=5, sku="SKU-100",
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(phone_number="09121234567", password="StrongPass123")


@pytest.mark.django_db
class TestCartViews:
    def test_add_to_cart_then_visible_in_cart_page(self, client, product):
        client.post(f"/cart/add/{product.id}/", {"quantity": 2})
        response = client.get("/cart/")
        assert response.status_code == 200
        assert product.name in response.content.decode()

    def test_cannot_add_out_of_stock_product(self, client, category):
        out_of_stock = Product.objects.create(
            name="محصول ناموجود", category=category, price=1000, stock=0, sku="SKU-OOS",
        )
        response = client.post(
            f"/cart/add/{out_of_stock.id}/", {"quantity": 1},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestCheckout:
    CHECKOUT_DATA = {
        "receiver_full_name": "علی رضایی",
        "receiver_phone_number": "09121234567",
        "province": "تهران",
        "city": "تهران",
        "postal_code": "1234567890",
        "full_address": "خیابان آزادی، پلاک ۱",
    }

    def test_checkout_requires_login(self, client, product):
        client.post(f"/cart/add/{product.id}/", {"quantity": 1})
        response = client.get("/checkout/")
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_successful_checkout_creates_order_and_decrements_stock(self, client, user, product):
        client.force_login(user)
        client.post(f"/cart/add/{product.id}/", {"quantity": 2})
        response = client.post("/checkout/", self.CHECKOUT_DATA)

        product.refresh_from_db()
        assert product.stock == 3
        order = Order.objects.get(user=user)
        assert order.items.count() == 1
        assert order.items.first().quantity == 2
        assert order.total == order.subtotal + order.shipping_cost
        assert response.status_code == 302  # redirected to payment request

    def test_checkout_blocks_when_stock_drops_below_cart_quantity(self, client, user, product):
        """Cart quantity was valid when added; another order (or an admin
        correction) then depletes stock before checkout completes. The
        checkout view re-validates stock under select_for_update at the
        time of purchase, not just at add-to-cart time."""
        client.force_login(user)
        client.post(f"/cart/add/{product.id}/", {"quantity": 5})  # equals current stock, allowed

        product.stock = 1
        product.save(update_fields=["stock"])

        client.post("/checkout/", self.CHECKOUT_DATA)

        product.refresh_from_db()
        assert product.stock == 1  # unchanged — order must not be fulfilled
        assert not Order.objects.filter(user=user).exists()
