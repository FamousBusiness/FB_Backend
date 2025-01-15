from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreCategoryViewSet, StoreHomePageBannerViewSet, StoreHomePageProductViewSet, StoreCategoryWiseProductViewSet, ProductServiceViewSet, CreateProductCartViewSet, CheckoutPageView, UserDeliveryAddressView, MultipleProductViewSet, UpdateCartQuantityView, CountCartProdctQuantityView, EcomRazorPayPaymentProcess, AllBusinessOrdersView, AllStoreCategoryViewSet, CheckProductAvailabilityView



router = DefaultRouter()


router.register(r'v1/store/category', StoreCategoryViewSet, basename='store_category')
router.register(r'v1/store/banner', StoreHomePageBannerViewSet, basename='store_banner')
router.register(r'v1/store/home/product', StoreHomePageProductViewSet, basename='store_home_product')
router.register(r'v1/category/product', StoreCategoryWiseProductViewSet, basename='store_category_product')
router.register(r'v1/product', ProductServiceViewSet, basename='store_product')
router.register(r'v1/cart', CreateProductCartViewSet, basename='cart_item')
router.register(r'v1/delivery/address', UserDeliveryAddressView, basename='delivery_address')
router.register(r'v1/all/store/categories', AllStoreCategoryViewSet, basename='all_store_categories')




urlpatterns = [
    path('', include(router.urls)),
    path('v1/checkout/', CheckoutPageView.as_view(), name='checkout'),
    path('v1/multiple/product', MultipleProductViewSet.as_view(), name='checkout'),
    path('v1/update/cart/', UpdateCartQuantityView.as_view(), name='update_cart'),
    path('v1/total/cart/quantity', CountCartProdctQuantityView.as_view(), name='update_cart'),
    path('v1/razorpay/payment', EcomRazorPayPaymentProcess.as_view(), name='razorpay_payment'),
    path('v1/all/business/orders', AllBusinessOrdersView.as_view(), name='all_business_orders'),
    path('v1/product/availability/check/', CheckProductAvailabilityView.as_view(), name='product_availability_check')
]
