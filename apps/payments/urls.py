from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("request/<int:order_id>/", views.request_payment, name="request_payment"),
    path("callback/<int:order_id>/", views.verify_payment, name="verify_payment"),
]
