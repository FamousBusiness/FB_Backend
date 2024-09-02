from django.contrib import admin
from .models import ChatModel, ChatNotification


class ChatModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'message')

class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'is_seen')


admin.site.register(ChatModel, ChatModelAdmin)
admin.site.register(ChatNotification, ChatNotificationAdmin)
