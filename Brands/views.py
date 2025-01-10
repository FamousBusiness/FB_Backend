from rest_framework.views import APIView
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from Listings.models import Business
from .serializers import (
    BrandBusinessSerializer, BrandProductSerializer, BrandSerializer, BrandProductCRUDSerializer,
    BrandProfilePageSerializer
    )
from .models import BrandProducts, BrandBusinessPage
from Listings.serializers import BusinessSerializer
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from .permissions import IsBrandOwnerPermission
from django.shortcuts import get_object_or_404





CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)



#Category wise Brands in Landing page
class BrandWiseBusinessAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   = PageNumberPagination


    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, brand=None):
        brand_page = get_object_or_404(BrandBusinessPage, brand_name__icontains=brand)
        
        try:
            businesses = Business.objects.filter(brand__brand_name__icontains=brand)
        except:
            return Response({'msg': 'No Business Page exist with given detail'})
        
        try:
            products = BrandProducts.objects.filter(brand__brand_name__icontains=brand)
        except:
            products = None

        business_page = self.paginate_queryset(businesses)
        product_page  = self.paginate_queryset(products)

        brand_product_serializer = BrandProductSerializer(product_page, many=True)
        brand_serializer         = BrandBusinessSerializer(brand_page)
        business_serializer      = BusinessSerializer(business_page, many=True)

        response_data = {
            'Business': business_serializer.data,
            'Brands': brand_serializer.data,
            'Brand_Products': brand_product_serializer.data
        }

        return self.get_paginated_response(response_data)

        



# Used in Landing Page
class CategoryWiseBrandView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id):
        # category_id = request.data.get('category_id')

        try:
            brands = BrandBusinessPage.objects.filter(category=category_id, trending=True)[:10]
        except Exception as e:
            return Response({'msg': f'Not able to found any brands related to this category {str(e)}'})
        
        brand_serializer = BrandSerializer(brands, many=True)

        return Response({'msg': 'Brand data fetched successfully', 'data': brand_serializer.data}, status=status.HTTP_200_OK)

    

class BrandProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsBrandOwnerPermission]
    queryset           = BrandProducts.objects.all()
    serializer_class   = BrandProductCRUDSerializer

    def get_queryset(self):
        brand_id = self.request.query_params.get('brand_id')
        if brand_id:
            return BrandProducts.objects.filter(brand=brand_id)
        return BrandProducts.objects.all()

    def create(self, request, *args, **kwargs):
        brand_id = request.data.get('brand_id')
        request.data['brand'] = brand_id

        return super().create(request, *args, **kwargs)
    



class BrandProductUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBrandOwnerPermission]
    
    def put(self, request, pk,*args, **kwargs):
        product_id = request.data.get('product_id')
      
        try:
            product = BrandProducts.objects.get(brand=pk, id=product_id)
        except BrandProducts.DoesNotExist:
            return Response({'msg': 'No Products Available with this details'})
        
        request.data['brand'] = pk

        serializer = BrandProductCRUDSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()   

        return Response({'msg': 'Product data updated Successfully'}, status=status.HTTP_200_OK)
    



class BrandProductDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsBrandOwnerPermission]

    def delete(self, request,*args, **kwargs):
        product_id = request.data.get('product_id')
        brand_id   = request.data.get('brand_id')
        try:
            product = BrandProducts.objects.get(brand=brand_id, id=product_id)
        except BrandProducts.DoesNotExist:
            return Response({'msg': 'No Products Available with this details'}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()

        return Response({'msg': 'Product Deleted Successfully'}, status=status.HTTP_200_OK)
    


class BrandProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, pk):
        brand_id = pk

        try:
            brand_profile = BrandBusinessPage.objects.get(id=brand_id)

        except BrandBusinessPage.DoesNotExist:
            return Response({'msg': 'Business Page Does Not exists with this name'})
        
        brand_serializer = BrandProfilePageSerializer(brand_profile)

        response_data = {
            'Brand_data': brand_serializer.data
        }
        # serializer = BusinessSerializer(business)
        return Response({'msg': 'Brand Profile data fetched succefully', 'data': response_data}, status=status.HTTP_200_OK)
    


    