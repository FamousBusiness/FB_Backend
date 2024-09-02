from django.urls import path
from .views import (BrandWiseBusinessAPIView, CategoryWiseBrandView, BrandProductListCreateView,
                     BrandProductUpdateView, BrandProductDeleteView, BrandProfileView)


urlpatterns = [
    path('<brand>/', BrandWiseBusinessAPIView.as_view(), name='brand-category-wise-business'),
    # path('all-brands/', AllBrandsAPIView.as_view(), name='all-brands'),
    path('category-wise-brand/<int:category_id>/', CategoryWiseBrandView.as_view(), name='category_wise_brands'),
    path('brand-product-create/', BrandProductListCreateView.as_view(), name='brand_product_create'),
    path('brand-product-update/<int:pk>/', BrandProductUpdateView.as_view(), name='brand_product_update'),
    path('brand-product-delete/', BrandProductDeleteView.as_view(), name='brand_product_delete'),
    path('brand-profile/<int:pk>/', BrandProfileView.as_view(), name='brand_product_delete'),
]


