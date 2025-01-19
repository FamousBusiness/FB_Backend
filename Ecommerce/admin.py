from django.contrib import admin
from .models import (
    StoreBanner, ProductTag, ProductOffers, ProductSpecification, EcommercePhonepeOrder,
    ProductImages, ProductOrders, Cart, UserAddress, EcomRazorPayOrders, EMIOffers, PinCode, RefundTransaction
)


@admin.register(ProductOrders)
class ProductOrdersModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'business', 'product', 'quantity', 'is_paid', 'order_id', 'payment_mode')
    ordering     = ('-id', )
    search_fields = ('order_id', )



admin.site.register(StoreBanner)
admin.site.register(ProductTag)
admin.site.register(ProductOffers)
admin.site.register(ProductSpecification)
admin.site.register(ProductImages)
admin.site.register(Cart)
admin.site.register(UserAddress)
admin.site.register(EcomRazorPayOrders)
admin.site.register(EMIOffers)
admin.site.register(PinCode)
admin.site.register(EcommercePhonepeOrder)
admin.site.register(RefundTransaction)
