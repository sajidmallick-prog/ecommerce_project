from django.contrib import admin
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'supplier', 'manufacturer', 'category', 'price', 'stock', 'cover_preview', 'created_at')
    search_fields = ('product_name', 'supplier__name', 'manufacturer__name', 'category__name')
    list_filter = ('supplier', 'manufacturer', 'category', 'created_at')
    ordering = ('-created_at',)
   
    def cover_preview(self, obj):
        """Display a small preview of the book cover image."""
        if obj.cover_image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;">', obj.cover_image.url)
        return "No Image"

    cover_preview.allow_tags = True
    cover_preview.short_description = "Cover Preview"

