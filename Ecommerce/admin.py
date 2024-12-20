from django.contrib import admin
from .models import StoreBanner, ProductTag, ProductOffers, ProductSpecification, ProductImages



admin.site.register(StoreBanner)
admin.site.register(ProductTag)
admin.site.register(ProductOffers)
admin.site.register(ProductSpecification)
admin.site.register(ProductImages)