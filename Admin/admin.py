from django.contrib import admin
from .models import AutoPayRequestSent, AutoPaySuccessResponse

# Register your models here.




@admin.register(AutoPayRequestSent)
class AutoRequestSentModelAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('user','transaction_id', 'premium_plan', 'is_sent')
    search_fields = ('user', 'transaction_id', 'is_sent')



@admin.register(AutoPaySuccessResponse)
class AutoPaySuccessResponse(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('user',)