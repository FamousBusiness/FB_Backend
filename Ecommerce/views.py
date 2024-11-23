from Listings.models import Category, ProductService, SubCategory
from .models import StoreBanner, ProductTag
from rest_framework import viewsets
from .serializers import (
    StoreHomePageCategorySerializer, StoreHomePageBannerSerializer, StoreHomePageProductSerializer, CategoryWiseProductSerializer,
    ProductServiceSerializer, StoreHomePageProductTagSerializer
    )
from .pagination import StoreHomepageProductPagination




#### Categories at the top of the Store Home page
class StoreCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StoreHomePageCategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_store = True)[:9]
    



#### Banners on Store Home page
class StoreHomePageBannerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StoreHomePageBannerSerializer

    def get_queryset(self):
        return StoreBanner.objects.all().order_by('-id')




### Homepage product pagination
class StoreHomePageProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StoreHomePageProductTagSerializer
    pagination_class = StoreHomepageProductPagination
    queryset = ProductTag.objects.filter(is_visible=True).prefetch_related('productservice_set')

    # def get_queryset(self):
        # return ProductService.objects.filter(product_tag__isnull=False, product_tag__is_visible=True)
    


#### Procts inside Category wise store page
class StoreCategoryWiseProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategoryWiseProductSerializer

    def get_queryset(self):
        category_id = self.request.query_params.get("category_id")
        subcategory_name = self.request.query_params.get("subcategory")

        ### Get the subcategory
        subcategory = SubCategory.objects.get(name = subcategory_name)

        queryset = ProductService.objects.all()

        if category_id:
            queryset = queryset.filter(category_id = category_id)

        if subcategory:
            queryset = queryset.filter(subcategory = subcategory)

        return queryset
    


### Product Page viewset
class ProductServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductServiceSerializer

    def get_queryset(self):
        product_id = self.request.query_params.get("product_id")

        ## Get the product by ID
        if product_id:
            return ProductService.objects.filter(pk=product_id)
        else:
            return ProductService.objects.none()  





