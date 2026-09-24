from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.orders.models import Order

from . import zarinpal
from .models import Payment


@login_required
def request_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != Order.Status.PENDING_PAYMENT:
        return redirect("orders:order_detail", pk=order.pk)

    try:
        authority, redirect_url = zarinpal.request_payment(request, order)
    except zarinpal.ZarinPalError:
        messages.error(request, "متأسفانه در حال حاضر امکان اتصال به درگاه پرداخت وجود ندارد. لطفاً بعداً تلاش کنید.")
        return redirect("orders:order_detail", pk=order.pk)

    Payment.objects.create(order=order, amount=order.total, authority=authority)
    return redirect(redirect_url)


@login_required
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    authority = request.GET.get("Authority")
    zarinpal_status = request.GET.get("Status")

    payment = order.payments.filter(authority=authority).first()

    if zarinpal_status != "OK" or not payment:
        if payment:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])
        messages.error(request, "پرداخت لغو شد یا ناموفق بود.")
        return render(request, "payments/failed.html", {"order": order, "meta_title": "پرداخت ناموفق", "noindex": True})

    is_success, ref_id = zarinpal.verify_payment(order, authority)
    if is_success:
        payment.status = Payment.Status.SUCCESS
        payment.ref_id = ref_id or ""
        payment.save(update_fields=["status", "ref_id"])
        order.status = Order.Status.PAID
        order.save(update_fields=["status"])
        return render(request, "payments/success.html", {
            "order": order, "ref_id": ref_id, "meta_title": "پرداخت موفق", "noindex": True,
        })

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])
    messages.error(request, "تأیید پرداخت ناموفق بود.")
    return render(request, "payments/failed.html", {"order": order, "meta_title": "پرداخت ناموفق", "noindex": True})
