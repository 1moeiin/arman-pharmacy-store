from django.contrib import admin

from .models import Brand, Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "order"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active", "order"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "brand", "price", "stock", "requires_prescription", "is_active", "is_featured"]
    list_filter = ["is_active", "is_featured", "requires_prescription", "category", "brand"]
    search_fields = ["name", "generic_name", "sku"]
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category", "brand"]
    inlines = [ProductImageInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "generic_name", "category", "brand", "sku")}),
        ("محتوا", {"fields": ("short_description", "description", "usage_instructions", "side_effects")}),
        ("قیمت و موجودی", {"fields": ("price", "compare_at_price", "stock", "requires_prescription")}),
        ("وضعیت", {"fields": ("is_active", "is_featured")}),
        ("سئو", {"fields": ("meta_title", "meta_description")}),
    )
