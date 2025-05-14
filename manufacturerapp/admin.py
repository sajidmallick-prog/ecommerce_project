from django.contrib import admin
from .models import Manufacturer

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'website')  # Show publisher name, contact, and website
    search_fields = ('name', 'contact')  # Enable search by name and contact
    list_filter = ('name',)  # Add filtering by name
    ordering = ('name',)  # Sort publishers alphabetically
