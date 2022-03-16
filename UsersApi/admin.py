from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'last_login', 'is_admin', 'is_active',)
    search_fields = ('email', 'phone',)
    readonly_fields = ('last_login',)
    filter_horizontal = ()
    list_filter = ('last_login',)
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('email', 'phone', 'password'),

        }),
    )

    ordering = ('email',)

admin.site.register(User, UserAdmin)
admin.site.register(OTPModel)
admin.site.register(Customer)
