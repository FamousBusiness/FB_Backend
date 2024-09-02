from django.contrib import admin
from Brands.models import BrandBusinessPage, BrandBanner, BrandProducts




class BrandBusinessPageModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand_name', 'business_name', 'email', 'mobile_number')


class BrandProductModelAdmin(admin.ModelAdmin):
    list_display = ('id','brand', 'name', 'price')    




admin.site.register(BrandBusinessPage, BrandBusinessPageModelAdmin)
admin.site.register(BrandProducts, BrandProductModelAdmin)
