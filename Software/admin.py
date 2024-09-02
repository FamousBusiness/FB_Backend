from django.contrib import admin
from .models import SoftwareOrder


class SoftwareOrdrerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'status', 'purchased_at']



admin.site.register(SoftwareOrder, SoftwareOrdrerModelAdmin)