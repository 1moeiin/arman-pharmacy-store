from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseServerError
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django_ratelimit.decorators import ratelimit

from apps.catalog.models import Category, Product

from .forms import ContactForm


def home(request):
    featured_products = (
        Product.objects.active().select_related("category", "brand").filter(is_featured=True)[:8]
    )
    new_products = Product.objects.active().select_related("category", "brand").order_by("-created_at")[:8]
    categories = Category.objects.filter(is_active=True, parent__isnull=True).order_by("order", "name")[:8]
    context = {
        "featured_products": featured_products,
        "new_products": new_products,
        "categories": categories,
        "meta_title": None,
        "meta_description": None,
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html", {
        "meta_title": "درباره ما",
        "meta_description": "آشنایی با داروخانه آرمان، سابقه فعالیت و تعهد ما به سلامت شما.",
    })


@ratelimit(key="ip", rate="10/h", method="POST", block=True)
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد. به‌زودی با شما تماس می‌گیریم.")
            return redirect("core:contact")
    else:
        form = ContactForm()
    return render(request, "core/contact.html", {
        "form": form,
        "meta_title": "تماس با ما",
        "meta_description": "راه‌های ارتباطی با داروخانه آرمان؛ تماس تلفنی، ایمیل و فرم پیام.",
    })


def search(request):
    query = request.GET.get("q", "").strip()
    results = Product.objects.none()
    if query:
        results = (
            Product.objects.active()
            .select_related("category", "brand")
            .filter(Q(name__icontains=query) | Q(generic_name__icontains=query) | Q(brand__name__icontains=query))
            .distinct()
        )
    paginator = Paginator(results, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "core/search_results.html", {
        "query": query,
        "page_obj": page_obj,
        "meta_title": f"نتایج جستجو برای «{query}»" if query else "جستجو",
        "meta_description": f"نتایج جستجوی محصولات دارویی و سلامت برای عبارت {query}" if query else "جستجوی محصولات",
        "noindex": True,  # search-result pages are thin/duplicate — keep out of the index
    })


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse("sitemap"))
    lines = [
        "User-agent: *",
        "Disallow: /accounts/",
        "Disallow: /cart/",
        "Disallow: /checkout/",
        "Disallow: /orders/",
        "Disallow: /admin/",
        "Disallow: /search/",
        f"Sitemap: {sitemap_url}",
    ]
    return TemplateResponse(request, "core/robots.txt", {"lines": lines}, content_type="text/plain")


def custom_404(request, exception=None):
    return render(request, "errors/404.html", {"meta_title": "صفحه پیدا نشد"}, status=404)


def custom_500(request):
    # A 500 can be caused by the database itself being unreachable, and our
    # context processors query the database (site settings) — rendering
    # this page must not depend on them, or a DB outage would break the
    # error page too. render_to_string(request=None) skips context processors.
    html = render_to_string("errors/500.html")
    return HttpResponseServerError(html)
