from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreCategoryViewSet, StoreHomePageBannerViewSet, StoreHomePageProductViewSet, StoreCategoryWiseProductViewSet, ProductServiceViewSet, CreateProductCartViewSet, CheckoutPageView, UserDeliveryAddressView, MultipleProductViewSet, UpdateCartQuantityView, CountCartProdctQuantityView, EcomRazorPayPaymentProcess, AllUserOrdersView, AllStoreCategoryViewSet, CheckProductAvailabilityView, OrderDetailView, AllBusinessOrdersView, EcomPhonepePaymentResponseView, UpdateOrderStatusView, EcomCODOrderAPIView



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
    path('v1/all/user/orders', AllUserOrdersView.as_view(), name='all_users_orders'),
    path('v1/all/business/orders', AllBusinessOrdersView.as_view(), name='all_business_orders'),
    path('v1/product/availability/check/', CheckProductAvailabilityView.as_view(), name='product_availability_check'),
    path('v1/order/detail/', OrderDetailView.as_view(), name='order_detail'),
    path('v1/updare/order/status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('v1/phonepe/payment/response/', EcomPhonepePaymentResponseView.as_view(), name='phonepe_payment_response'), ### For prepaid order
    path('v1/ecom/cod/order/', EcomCODOrderAPIView.as_view(), name='ecom_cod_order'), ### COF Order Place
]

