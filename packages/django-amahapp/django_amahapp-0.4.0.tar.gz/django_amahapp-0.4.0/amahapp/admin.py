
from django.contrib import admin
from .models import UserActivityLog

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'path', 'ip_address', 'method', 'timestamp', 'duration')
    list_filter = ('method', 'timestamp')
    search_fields = ('path', 'ip_address', 'user__username')
from django.contrib import admin

# Register your models here.
