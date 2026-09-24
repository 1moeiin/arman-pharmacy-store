from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Category, Product

PAGE_SIZE = 24


def product_list(request):
    products = Product.objects.active().select_related("category", "brand").prefetch_related("images")
    products = _apply_sort(products, request.GET.get("sort"))
    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by("order", "name")
    return render(request, "catalog/product_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "meta_title": "همه محصولات",
        "meta_description": "مشاهده و خرید انواع داروها و محصولات سلامت از داروخانه آرمان.",
    })


def category_detail(request, slug):
    category = get_object_or_404(Category.objects.filter(is_active=True), slug=slug)
    subcategory_ids = list(category.children.filter(is_active=True).values_list("id", flat=True))
    products = (
        Product.objects.active()
        .select_related("category", "brand")
        .prefetch_related("images")
        .filter(category_id__in=[category.id, *subcategory_ids])
    )
    products = _apply_sort(products, request.GET.get("sort"))
    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "catalog/category_detail.html", {
        "category": category,
        "page_obj": page_obj,
        "meta_title": category.seo_title,
        "meta_description": category.seo_description,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.active().select_related("category", "brand").prefetch_related("images"),
        slug=slug,
    )
    related_products = (
        Product.objects.active()
        .select_related("category", "brand")
        .filter(category=product.category)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, "catalog/product_detail.html", {
        "product": product,
        "related_products": related_products,
        "meta_title": product.seo_title,
        "meta_description": product.seo_description,
    })


def _apply_sort(queryset, sort_key):
    return {
        "price_asc": queryset.order_by("price"),
        "price_desc": queryset.order_by("-price"),
        "newest": queryset.order_by("-created_at"),
    }.get(sort_key, queryset)
