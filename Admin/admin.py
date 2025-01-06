from django.contrib import admin
from .models import AutoPayRequestSent, AutoPaySuccessResponse

# Register your models here.




@admin.register(AutoPayRequestSent)
class AutoRequestSentModelAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('user','transaction_id', 'premium_plan', 'is_sent', 'sent_date')
    search_fields = ('user__name', 'transaction_id', 'is_sent')



@admin.register(AutoPaySuccessResponse)
class AutoPaySuccessResponse(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('user', 'premium_plan', 'is_success', 'created_date', 'status', )
    search_fields = ('is_success', 'created_date', 'user__name', 'status', )
