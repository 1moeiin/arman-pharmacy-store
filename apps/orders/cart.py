from decimal import Decimal

from apps.catalog.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """Session-backed cart. Works for anonymous visitors (no account needed
    to browse/add to cart — good for conversion and lets crawlers/users
    reach product pages with zero friction); login is only required at
    checkout, where the cart becomes a persisted Order."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product: Product, quantity: int = 1, replace: bool = False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": 0}
        if replace:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.cart[product_id]["quantity"] = max(1, min(self.cart[product_id]["quantity"], product.stock or 1))
        self.save()

    def remove(self, product: Product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.active().select_related("category").filter(id__in=product_ids)
        products_by_id = {str(p.id): p for p in products}
        for product_id, item in self.cart.items():
            product = products_by_id.get(product_id)
            if not product:
                continue
            quantity = item["quantity"]
            yield {
                "product": product,
                "quantity": quantity,
                "line_total": product.price * quantity,
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def subtotal(self) -> Decimal:
        return sum((entry["line_total"] for entry in self), Decimal("0"))

    @property
    def requires_prescription(self) -> bool:
        return any(entry["product"].requires_prescription for entry in self)

    @property
    def is_empty(self) -> bool:
        return len(self.cart) == 0
