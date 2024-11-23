from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreCategoryViewSet, StoreHomePageBannerViewSet, StoreHomePageProductViewSet, StoreCategoryWiseProductViewSet, ProductServiceViewSet


router = DefaultRouter()
router.register(r'v1/store/category', StoreCategoryViewSet, basename='store_category')
router.register(r'v1/store/banner', StoreHomePageBannerViewSet, basename='store_banner')
router.register(r'v1/store/home/product', StoreHomePageProductViewSet, basename='store_home_product')
router.register(r'v1/category/product', StoreCategoryWiseProductViewSet, basename='store_category_product')
router.register(r'v1/product', ProductServiceViewSet, basename='store_product')


urlpatterns = [
    path('', include(router.urls)),
]
