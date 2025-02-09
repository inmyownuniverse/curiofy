#from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role']

    def get_queryset(self, request):
        """ Restrict non-admins from viewing other users. """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(role=request.user.role)
        return qs

    def has_delete_permission(self, request, obj=None):
        """ Allow only admins to delete users. """
        return request.user.role == 'admin'

admin.site.register(CustomUser, CustomUserAdmin)
