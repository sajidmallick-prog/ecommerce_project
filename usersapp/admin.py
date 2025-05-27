from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'phone', 'user_type')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    list_filter = ('user_type',)
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'username', 'phone', 'profile_picture')
        }),
    )
