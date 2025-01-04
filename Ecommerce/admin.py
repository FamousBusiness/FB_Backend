from django.contrib import admin
from .models import (
    StoreBanner, ProductTag, ProductOffers, ProductSpecification, 
    ProductImages, ProductOrders, Cart, UserAddress, EcomRazorPayOrders
)




admin.site.register(StoreBanner)
admin.site.register(ProductTag)
admin.site.register(ProductOffers)
admin.site.register(ProductSpecification)
admin.site.register(ProductImages)
admin.site.register(ProductOrders)
admin.site.register(Cart)
admin.site.register(UserAddress)
admin.site.register(EcomRazorPayOrders)
