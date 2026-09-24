from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["order", "amount", "status", "ref_id", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order__id", "authority", "ref_id"]
    readonly_fields = ["order", "amount", "authority", "ref_id", "status", "created_at", "updated_at"]

    def has_add_permission(self, request):
        return False
