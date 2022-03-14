from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


class MyUserAdmin(BaseUserAdmin):
    list_display = ('first_name', 'last_name', 'email',
                    'last_login', 'is_admin', 'is_active',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('last_login',)
    filter_horizontal = ()
    list_filter = ('last_login',)
    fieldsets = ()

    add_fieldsets = (
        (None, {
            'classes': ('wide'),
            'fields': ('email', 'phone', 'first_name', 'middle_name', 'last_name', 'password'),

        }),
    )

    ordering = ('email',)


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(OTPModel)
