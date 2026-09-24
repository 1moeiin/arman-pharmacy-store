from django.urls import path, register_converter

from . import views
from .converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "uslug")

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("category/<uslug:slug>/", views.category_detail, name="category_detail"),
    path("<uslug:slug>/", views.product_detail, name="product_detail"),
]
