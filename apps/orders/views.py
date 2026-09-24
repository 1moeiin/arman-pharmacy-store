from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.catalog.models import Product

from .cart import Cart
from .forms import CheckoutForm
from .models import OrderItem

SHIPPING_COST = 50000  # تومان — ثابت برای نسخه اول، بعداً قابل تنظیم در تنظیمات سایت


def cart_detail(request):
    return render(request, "orders/cart.html", {
        "meta_title": "سبد خرید",
        "noindex": True,
    })


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product.objects.active(), id=product_id)
    cart = Cart(request)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1
    if not product.in_stock:
        message = "این محصول موجود نیست."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": message}, status=400)
        messages.error(request, message)
        return redirect(product.get_absolute_url())

    cart.add(product, quantity=quantity)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "cart_count": len(cart), "cart_subtotal": int(cart.subtotal)})
    messages.success(request, f"{product.name} به سبد خرید اضافه شد.")
    return redirect(request.POST.get("next") or "orders:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product.objects.active(), id=product_id)
    cart = Cart(request)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1
    cart.add(product, quantity=quantity, replace=True)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "cart_count": len(cart), "cart_subtotal": int(cart.subtotal)})
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product.objects.active(), id=product_id)
    cart = Cart(request)
    cart.remove(product)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "cart_count": len(cart), "cart_subtotal": int(cart.subtotal)})
    messages.info(request, "محصول از سبد خرید حذف شد.")
    return redirect("orders:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    if cart.is_empty:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect("catalog:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                locked_products = {
                    p.id: p
                    for p in Product.objects.select_for_update().filter(
                        id__in=[entry["product"].id for entry in cart]
                    )
                }
                for entry in cart:
                    product = locked_products[entry["product"].id]
                    if entry["quantity"] > product.stock:
                        form.add_error(None, f"موجودی «{product.name}» کافی نیست.")
                        break
                else:
                    order = form.save(commit=False)
                    order.user = request.user
                    order.shipping_cost = SHIPPING_COST
                    order.requires_prescription_review = cart.requires_prescription
                    order.save()
                    for entry in cart:
                        product = locked_products[entry["product"].id]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            unit_price=product.price,
                            quantity=entry["quantity"],
                        )
                        product.stock -= entry["quantity"]
                        product.save(update_fields=["stock"])
                    order.recalculate_totals()
                    order.save(update_fields=["subtotal", "total"])
                    cart.clear()
                    return redirect("payments:request_payment", order_id=order.id)
    else:
        initial = {}
        default_address = request.user.addresses.filter(is_default=True).first()
        if default_address:
            initial = {
                "receiver_full_name": default_address.receiver_full_name,
                "receiver_phone_number": default_address.receiver_phone_number,
                "province": default_address.province,
                "city": default_address.city,
                "postal_code": default_address.postal_code,
                "full_address": default_address.full_address,
            }
        form = CheckoutForm(initial=initial)

    return render(request, "orders/checkout.html", {
        "form": form,
        "cart": cart,
        "shipping_cost": SHIPPING_COST,
        "meta_title": "تسویه حساب",
        "noindex": True,
    })


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "orders/order_list.html", {
        "orders": orders,
        "meta_title": "سفارش‌های من",
        "noindex": True,
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(request.user.orders.prefetch_related("items__product"), pk=pk)
    return render(request, "orders/order_detail.html", {
        "order": order,
        "meta_title": f"سفارش #{order.pk}",
        "noindex": True,
    })
