from rest_framework.response import Response
from rest_framework import status
from Listings.models import Category, ProductService, SubCategory
from .models import StoreBanner, ProductTag
from rest_framework import viewsets
from .serializers import (
    StoreHomePageCategorySerializer, StoreHomePageBannerSerializer, CategoryWiseProductSerializer,
    ProductServiceSerializer, StoreHomePageProductTagSerializer
    )
from .pagination import StoreHomepageProductPagination, StoreCategoryWiseProductViewSetPagination
from django.core.exceptions import ObjectDoesNotExist




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
    pagination_class = StoreCategoryWiseProductViewSetPagination

    def get_queryset(self):
        category_id = self.request.query_params.get("category_id")
        subcategory_name = self.request.query_params.get("subcategory")

        if not category_id:
            return Response({"error": "category_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = ProductService.objects.all()

        queryset = queryset.filter(category_id=category_id)

        if subcategory_name:
            try:
                subcategory = SubCategory.objects.get(name=subcategory_name)
                queryset = queryset.filter(subcategory=subcategory)
            except ObjectDoesNotExist:
                return Response({"error": f"SubCategory with name '{subcategory_name}' does not exist."},status=status.HTTP_404_NOT_FOUND)

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





