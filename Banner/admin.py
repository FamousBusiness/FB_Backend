from django.contrib import admin
from Banner.models import Banner




class BannerModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state', 'city', 'verified', 'expired', 'category')
    empty_value_display = "-empty-"




admin.site.register(Banner, BannerModelAdmin)