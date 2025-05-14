from django.contrib import admin
from django.utils.html import format_html
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'nationality', 'city')
    search_fields = ('name', 'nationality')
    list_filter = ('nationality', 'city')
    ordering = ('name',)
   

   