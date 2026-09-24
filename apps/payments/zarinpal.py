"""Thin client for ZarinPal's REST payment gateway.

Docs: https://docs.zarinpal.com/paymentGateway/
Amounts are in Toman throughout this project; ZarinPal's v4 REST API also
expects Toman when currency="IRT" is passed explicitly.
"""
import logging

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger("apps.payments")

SANDBOX_BASE = "https://sandbox.zarinpal.com/pg/v4/payment/"
LIVE_BASE = "https://payment.zarinpal.com/pg/v4/payment/"
SANDBOX_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"
LIVE_STARTPAY = "https://payment.zarinpal.com/pg/StartPay/"

REQUEST_TIMEOUT = 10  # seconds — never block a web worker indefinitely on a flaky upstream


class ZarinPalError(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


def _base_url():
    return SANDBOX_BASE if settings.ZARINPAL_SANDBOX else LIVE_BASE


def _startpay_url():
    return SANDBOX_STARTPAY if settings.ZARINPAL_SANDBOX else LIVE_STARTPAY


def request_payment(request, order, description=""):
    """Ask ZarinPal for an authority code and return the redirect URL."""
    callback_url = request.build_absolute_uri(reverse("payments:verify_payment", args=[order.id]))
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(order.total),
        "currency": "IRT",
        "description": description or f"سفارش #{order.id}",
        "callback_url": callback_url,
        "metadata": {"mobile": order.receiver_phone_number, "order_id": order.id},
    }
    try:
        response = requests.post(f"{_base_url()}request.json", json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json().get("data", {})
    except requests.RequestException as exc:
        logger.error("ZarinPal request failed for order %s: %s", order.id, exc)
        raise ZarinPalError("ارتباط با درگاه پرداخت برقرار نشد.") from exc

    if not data or data.get("code") != 100:
        errors = response.json().get("errors", {})
        logger.error("ZarinPal rejected request for order %s: %s", order.id, errors)
        raise ZarinPalError("درگاه پرداخت درخواست را رد کرد.", code=errors.get("code"))

    authority = data["authority"]
    return authority, f"{_startpay_url()}{authority}"


def verify_payment(order, authority):
    """Confirm a completed payment. Returns (is_success, ref_id_or_None)."""
    payload = {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "amount": int(order.total),
        "authority": authority,
    }
    try:
        response = requests.post(f"{_base_url()}verify.json", json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json().get("data", {})
    except requests.RequestException as exc:
        logger.error("ZarinPal verify failed for order %s: %s", order.id, exc)
        return False, None

    if data and data.get("code") in (100, 101):
        return True, data.get("ref_id")
    return False, None
