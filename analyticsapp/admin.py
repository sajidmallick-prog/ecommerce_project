from django.contrib import admin
from .models import SalesSnapshot, ProductPerformance, CustomerBehavior

@admin.register(SalesSnapshot)
class SalesSnapshotAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'order_count', 'avg_order_value', 'refunds')
    list_filter = ('date',)
    search_fields = ('date',)
    ordering = ('-date',)

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'views', 'cart_additions', 'purchases', 'revenue', 'conversion_rate_display')
    list_filter = ('date', 'product')
    search_fields = ('product__name', 'date')
    ordering = ('-date', '-revenue')
    
    def conversion_rate_display(self, obj):
        return f"{obj.conversion_rate:.2f}%"
    conversion_rate_display.short_description = 'Conversion Rate'
    conversion_rate_display.admin_order_field = 'conversion_rate'

@admin.register(CustomerBehavior)
class CustomerBehaviorAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'session_key', 'first_product_view', 'entry_point', 'timestamp', 'converted', 'conversion_value')
    list_filter = ('converted', 'timestamp')
    search_fields = ('user__username', 'session_key', 'first_product_view__name')
    ordering = ('-timestamp',)
    
    def user_display(self, obj):
        return obj.user.username if obj.user else "Anonymous"
    user_display.short_description = 'User'
    
    def first_product(self, obj):
        return obj.first_product_view.name if obj.first_product_view else "None"
    first_product.short_description = 'First Product Viewed'