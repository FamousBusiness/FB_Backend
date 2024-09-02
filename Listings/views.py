from rest_framework.views import APIView
from Listings.models import (
    Business, Category, FrontCarousel, SubCategory, ProductService, CategoryWiseBusinessSideImage,
    BusinessMobileNumbers, BusinessImage, BusinessPageLike, BusinessPageReviewRating, FooterImage
)
from ADS.models import ADS, UserADView
from Banner.models import Banner
from Brands.models import BrandBusinessPage
from Lead.models import ComboLead, Lead, LeadPrice
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    BrandBusinessSerializer, BusinessSerializer, CategorySerializer, LandingPageBrandSerializer,
    SingleListingsSerializer,BannerSerializer, 
    FrontCarouselSerializer, CategoryWiseBusinessSideImageSerializer,
    BusinessMobileSerializer, CategoryLeadGenerateSerializer, CategorywiseBusinessSerilizer,
    IDwiseBusinessSerilizer, FootImageSerializer, UserSpecificBusinessPageSerializer, ProductServiceCRUDSerializer
    )
from Lead.serializer import ComboLeadSerializer
from Listings.ADS.ads_serializers import AdSerializer
from rest_framework import permissions
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import timedelta
from .serializers import ImageSerializer
from Listings.models import Image
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, IntegerField, When, Case
from django.utils.decorators import method_decorator





CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)




def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# @method_decorator(ensure_csrf_cookie, name='dispatch')
class LandingPageAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   =  PageNumberPagination
    

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, *args, **kwargs):

        try:
             city     = request.GET.get('city')
             state    = request.GET.get('state')
             pincode  = request.GET.get('pincode')
             locality = request.GET.get('locality')

            #  if not (city or state or pincode or locality):
            #      return Response ({'msg': 'Please provide any address to send data'})
             
             if locality:
                 verified_business = Business.objects.filter(locality=locality, verified=True)[:20]
                 if verified_business.exists():
                     businesses = verified_business
                 businesses = Business.objects.filter(locality=locality)[:20]
             elif pincode:
                 verified_business = Business.objects.filter(pincode=pincode, verified=True)[:20]
                 if verified_business.exists():
                     businesses = verified_business
                 businesses = Business.objects.filter(pincode=pincode)[:20]
             elif city:
                 verified_business = Business.objects.filter(city=city, verified=True)[:20]
                 if verified_business.exists():
                     businesses = verified_business
                 businesses = Business.objects.filter(city=city)[:20]
             elif state:
                 verified_business = Business.objects.filter(state=state, verified=True)[:20]
                 if verified_business.exists():
                     businesses = verified_business
                 businesses = Business.objects.filter(state=state)[:20]
             else:
                 verified_business = Business.objects.filter(verified=True)[:20]
                 
                 if verified_business.exists():
                    businesses = verified_business
                 businesses = Business.objects.all()[:20]
                 

             brands                 = BrandBusinessPage.objects.all()[:20]
             ads                    = ADS.objects.filter(verified=True, is_active=True, city=city)[:20]
             banner                 = Banner.objects.filter(verified=True, expired=False)[:20]
             carousel               = FrontCarousel.objects.all()
             combo_leads            = ComboLead.objects.all()
             mobile_number_ads_user = [ad.posted_by.mobile_number for ad in ads]

        except ModuleNotFoundError:
            return Response({'msg': 'No data found'})
        
        ads_serializer      = AdSerializer(ads, many=True)

        for ad_data, mobile_number in zip(ads_serializer.data, mobile_number_ads_user):
            ad_data['mobile_number'] = mobile_number

        business_page = self.paginate_queryset(businesses)
        banner_page   = self.paginate_queryset(banner)
        carousel_page = self.paginate_queryset(carousel)
        brand_page    = self.paginate_queryset(brands)
        combo_page    = self.paginate_queryset(combo_leads)

        business_serializer   = BusinessSerializer(business_page, many=True)
        banner_serializer     = BannerSerializer(banner_page, many=True)
        carousel_serializer   = FrontCarouselSerializer(carousel_page, many=True)
        brand_serializer      = LandingPageBrandSerializer(brand_page, many=True)
        combo_lead_serializer = ComboLeadSerializer(combo_page, many=True)

        # business_serializer = BusinessSerializer(businesses, many=True)
        # banner_serializer   = BannerSerializer(banner, many=True)
        # carousel_serializer = FrontCarouselSerializer(carousel, many=True)
        # brand_serializer    = LandingPageBrandSerializer(brands, many=True)
        # combo_lead_serializer = ComboLeadSerializer(combo_leads, many=True)
        
        response_data = {
            'Business': business_serializer.data,
            'ads': ads_serializer.data,
            'banner': banner_serializer.data,
            # 'jobs': jobs_serializer.data,
            'Carousel': carousel_serializer.data,
            'brands': brand_serializer.data,
            'combo_leads': combo_lead_serializer.data
        }

        return self.get_paginated_response(response_data)
        # return Response({'msg': 'All Business,Ads,Banners,Jobs data', 'data': response_data})
    


#Show All Business Page In landing Page
class BusinessAPIView(APIView):
    permission_classes = [permissions.AllowAny,]

    # @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        business = Business.objects.all()
        serializer = BusinessSerializer(business, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)





class CreateBusinessPageAPiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = BusinessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Business Page Created Successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        



class CategoryWiseBusinessAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   = PageNumberPagination 
    serializer_class   = CategorywiseBusinessSerilizer
    

    def can_create_lead(self, user, category):
      current_time = timezone.now()

      six_hours_ago = current_time - timedelta(hours=6)
      
      try:
        existing_leads = Lead.objects.filter(created_by=user, category=category, created_at__gte=six_hours_ago).exists()
      except:
          pass

      return not existing_leads

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, city=None, category=None): 
        #state=None,
        #Lead Generate
        try:
            user = request.user

            if user.is_authenticated:
                lead_category   = Category.objects.get(type=category) if category else None

                serializer_data = {'category': lead_category.pk if lead_category else None}
                lead_serializer = CategoryLeadGenerateSerializer(data=serializer_data)
                
                try:
                    lead_price = LeadPrice.objects.get(id=1)
                except Exception:
                    lead_price  = 10
                    
                lead_serializer.is_valid(raise_exception=True)

                if lead_category and not self.can_create_lead(user, lead_category):
                    return Response({'msg': 'Cannot create lead in the same category within 6 hours'}, status=status.HTTP_201_CREATED)
                else:
                    requirements = f'{lead_category.type} Requirements'

                    # lead_data = {
                    #     'created_by': user,
                    #     'mobile_number': user.mobile_number if user.mobile_number else None,
                    #     'email': user.email if user.email else None,
                    #     'city': city,
                    #     'status': 'Open',
                    #     'price': lead_price,
                    #     'requirement': requirements,
                    #     'category_lead': True
                    # }
                    
                    # lead_serializer.save(**lead_data)
                   
                    return Response({'msg': 'Lead Created Successfully'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("User is not Authenticated")
        
        finally:
            if category:
                try:
                    category_wise_business = Business.objects.filter(category__type__icontains=category)
                    banner   = Banner.objects.filter(category__type=category, verified=True, expired=False)
                except Business.DoesNotExist:
                    return Response({'msg': 'Business and Banner does not exist in this category'})
                
                if city:
                    try:
                        city_wise_business = category_wise_business.filter(city__icontains=city)
                        banner   = banner.filter(city__icontains=city, verified=True, expired=False)
                    except Business.DoesNotExist:
                        return Response({'msg': 'No Business Exist in this city'})
                    
                banner = banner[:10]

                try:
                    side_images = CategoryWiseBusinessSideImage.objects.filter(category__type=category)
                except:
                    side_images = None
                
                #Pagination to Business Page
                businesses = city_wise_business.annotate(
                    true_count=Sum(
                        Case(
                            When(verified=True, then=1),
                            When(trusted=True, then=1),
                            When(trending=True, then=1),
                            When(authorized=True, then=1),
                            When(industry_leader=True, then=1),
                            When(sponsor=True, then=1),
                            When(super=True, then=1),
                            When(premium=True, then=1),
                            default=0,
                            output_field=IntegerField()
                        )
                    )
                )
                ordered_business = businesses.order_by('-true_count')
                business_page = self.paginate_queryset(ordered_business)

                business_category_serializer = self.get_serializer(business_page, many=True)
                banner_category_serializer   = BannerSerializer(banner, many=True)
                side_images_serializer       = CategoryWiseBusinessSideImageSerializer(side_images, many=True)

                response_data = {
                    'category_wise_business': business_category_serializer.data,
                    'category_wise_banner':   banner_category_serializer.data,
                    'side_images':            side_images_serializer.data
                }

                if (ordered_business or banner):
                    return self.get_paginated_response(response_data)
                # elif banner:
                #     return Response({'msg': 'Data fetched Successfully', 'category_wise_banner':banner_category_serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({'msg': 'No Business Found in this detail'})
                
        return Response({'msg': 'Did not get any category field'}) 





class IDWiseBusinessAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(CACHE_TTL))
    def post(self, request, pk):
        business_id = pk

        try:
            business = Business.objects.get(id=business_id)
            
        except Business.DoesNotExist:
            return Response({'msg': 'Business Page Does Not exists with this name'})
        
        business_serializer = IDwiseBusinessSerilizer(business)

        response_data = {
            'Business_data': business_serializer.data
        }
        # serializer = BusinessSerializer(business)
        return Response({'msg': 'Success', 'data': response_data}, status=status.HTTP_200_OK)




class BusinessPageUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, business_id):
        user = request.user
        extra_mobile_numbers = request.data.get('mobile_numbers')
        email         = request.data.get('email')
        mobile_number = request.data.get('mobile_number')

        try:
            business = Business.objects.get(id=business_id)
            if business.owner == user:
                serializer    = UserSpecificBusinessPageSerializer(business, data=request.data)
                
                # if Business.objects.exclude(id=business_id).filter(Q(email=email) | Q(mobile_number=mobile_number)).exists():
                #     return Response({"msg": "Mobile and Email Already Exists"})
                
                if serializer.is_valid():
                    serializer.save()

                    if extra_mobile_numbers:
                        for mobile_numbers in extra_mobile_numbers:
                            business_page_mobile_numbers = BusinessMobileNumbers.objects.create(business_id=business_id, mobile_number=mobile_numbers)
                        
                    return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
            
            elif user.is_staff:
                serializer = UserSpecificBusinessPageSerializer(business, data=request.data)
                email         = request.data.get('email')
                mobile_number = request.data.get('mobile_number')

                # if Business.objects.exclude(id=business_id).filter(Q(email=email) | Q(mobile_number=mobile_number)).exists():
                #     return Response({"msg": "Mobile and Email Already Exists"})
                
                if serializer.is_valid():
                    serializer.save()

                    if extra_mobile_numbers:
                        for mobile_numbers in extra_mobile_numbers:
                            business_page_mobile_numbers = BusinessMobileNumbers.objects.create(business_id=business_id, mobile_number=mobile_numbers)
                        
                    return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({'msg': "Only the page owner can edit the page"})

        except Business.DoesNotExist:
            if user.is_staff:
                serializer = UserSpecificBusinessPageSerializer(business, data=request.data)
                email         = request.data.get('email')
                mobile_number = request.data.get('mobile_number')
                extra_mobile_numbers = request.data.get('mobile_numbers')

                # if Business.objects.exclude(id=business_id).filter(Q(email=email) | Q(mobile_number=mobile_number)).exists():
                #     return Response({"msg": "Mobile and Email Already Exists"})
                
                if serializer.is_valid():
                    serializer.save()

                    if extra_mobile_numbers:
                        for mobile_numbers in extra_mobile_numbers:
                            business_page_mobile_numbers = BusinessMobileNumbers.objects.create(business_id=business_id, mobile_number=mobile_numbers)
                    
                    return Response({'msg': 'Updated Successfully'}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'msg': 'Not able to update the page'}, status=status.HTTP_404_NOT_FOUND)



#Business Page Image Create and update by Page owner
class BusinessPageImageCreateUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # parser_classes      = [FormParser]
    
    def put(self, request, pk, *args, **kwargs):
        # business_id = request.data.get('business_id')
        img_id      = request.GET.getlist('img_id')
        images      = request.FILES.getlist('image')
        images_data = [{'image': i} for i in images]

        skipped_images = []
        if img_id:
            for image_id, image_data in zip(img_id, images_data):
                try:
                    image = Image.objects.get(id=image_id)
                    img_serializer = ImageSerializer(instance=image, data=image_data)
                    img_serializer.is_valid(raise_exception=True)
                    saved_images = img_serializer.save()
                    business_image, _ = BusinessImage.objects.get_or_create(business_id=pk)

                    if business_image.image.filter(id=image_id).exists():
                        business_image.image.remove(image)
                        business_image.image.add(saved_images)
                    else:
                        skipped_images.append(image_id)

                except Image.DoesNotExist:
                    return Response({'error': f'Image with ID {image_id} not found'}, status=status.HTTP_404_NOT_FOUND)
                
            return Response({'msg': 'Image Updated Succefully', 'Skipped Image id': skipped_images})  
        else:
            images = request.FILES.getlist('image')
            images_data = [{'image': i} for i in images]
            image_serializer = ImageSerializer(data=images_data, many=True)
            # image_serializer.is_valid(raise_exception=True)
            # saved_images = image_serializer.save()
            # BusinessImage.objects.get_or_create(business_id=pk)
            # business_image.image.set(saved_images)
        
        return Response({'msg': 'Success - Existing BusinessImage updated'})
    
    def post(self, request, pk, *args, **kwargs):

        try:
            images             = request.FILES.getlist('image')
            images_data        = [{'image': i} for i in images]
            print(images_data)
            image_serializer   = ImageSerializer(data=images_data, many=True)
            image_serializer.is_valid(raise_exception=True)
            saved_images       = image_serializer.save()
            business_image, _  = BusinessImage.objects.get_or_create(business_id=pk)
            business_image.image.add(*saved_images)
            return Response({'msg': 'Image Saved Successfully'})
        except Image.DoesNotExist:
            return Response({'msg': 'Invalid Image'})


   
class CategoryViewAPIView(APIView): 
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response({'status': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)




class CategoryUploadUpdateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        seralizer = CategorySerializer(data=request.data)
        seralizer.is_valid(raise_exception=True)
        seralizer.save()
        return Response({'msg': 'Category Uploaded Successfully'}, status=status.HTTP_200_OK)
        
    def put(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'Msg': 'No Category exist in this Name'})
        
        serializer = CategorySerializer(category, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Msg': "Category updated Successfully"})
    
        
    


class SingleListingAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = SingleListingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Data Saved Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'Invalid Input'})



class BusinessPageSearchAPiView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   = PageNumberPagination
    serializer_class   = BusinessSerializer
    
    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request, slug, *args, **kwargs):
        searched_city = request.GET.get("city")
        search_text = slug

        # city = request.query_params.get('')
        q_objects = (
            Q(keywords__icontains=search_text) |
            Q(services__icontains=search_text) |
            Q(business_info__icontains=search_text) |
            Q(business_name__icontains=search_text) |
            Q(GSTIN__icontains=search_text) |
            Q(CIN_No__icontains=search_text) |
            Q(company_No__icontains=search_text) | 
            Q(city__icontains=search_text) 
        )

        q2_objects = (
            Q(type__icontains = search_text) |
            Q(B2B2C__icontains = search_text) 
        )

        q3_objects = (
            Q(name__icontains = search_text)
        )

        combined_q_objects         = q_objects
        cat_combined_q_objects     = q2_objects
        sub_cat_combined_q_objects = q3_objects

        results             = Business.objects.filter(combined_q_objects, city=searched_city)
        cat_results         = Category.objects.filter(cat_combined_q_objects)
        subcategory_results = SubCategory.objects.filter(sub_cat_combined_q_objects)

        business_cat_results     = Business.objects.filter(category__in    = cat_results, city=searched_city)
        business_sub_cat_results = Business.objects.filter(subcategory__in = subcategory_results, city=searched_city)

        page            = self.paginate_queryset(results)
        cat_page        = self.paginate_queryset(business_cat_results)
        sub_cat_results = self.paginate_queryset(business_sub_cat_results)

        serializer                   = self.get_serializer(page, many=True)
        business_category_serializer = self.get_serializer(cat_page, many=True)
        business_sub_cat_serializer  = self.get_serializer(sub_cat_results, many=True) 

        resonse_data = {
            'business_data': serializer.data,
            'business_data_cat': business_category_serializer.data,
            'business_data_subcat': business_sub_cat_serializer.data
        }

        return self.get_paginated_response({'msg': 'All the searched data', 'data': resonse_data})
    


class BusinessMobileNumber(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        business_id = pk

        mobile_numbers = BusinessMobileNumbers.objects.filter(business_name_id=business_id)
        serializer = BusinessMobileSerializer(mobile_numbers, many=True)

        return Response({'msg': 'Fetched Successfully', 'data': serializer.data})



    
class BusinessPageLikesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, business_page_id):
        user = request.user

        try:
            business_page_instance = Business.objects.get(id=business_page_id)
        except Business.DoesNotExist:
            return Response({'msg': 'Business Page not found'}, status=status.HTTP_404_NOT_FOUND)
        
        existings_likes = BusinessPageLike.objects.filter(user=user, business_page=business_page_instance).first()
        
        if existings_likes:
            existings_likes.delete()
            return Response({'msg': 'Success'}, status=status.HTTP_200_OK)
        
        like = BusinessPageLike(user=user, business_page=business_page_instance)
        like.likes += 1
        like.save()

        return Response({'msg': 'Liked Successfully'}, status=status.HTTP_201_CREATED)
    



class BusinessPageReviewRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, business_id):
        review = request.data.get('review')
        user = request.user
        rating = request.data.get('rating')

        if not rating:
            rating = 3
            
        try:
            business_page_instance = Business.objects.get(id=business_id)
        except Business.DoesNotExist:
            return Response({'msg': 'Business Page not found'}, status=status.HTTP_404_NOT_FOUND)
        
        BusinessPageReviewRating.objects.create(user=user, rating=rating, review=review, business_page=business_page_instance)

        return Response({'msg': 'Posted Succefully'}, status=status.HTTP_201_CREATED)



class FooterImageAPiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        footer_images = FooterImage.objects.all()

        serializer = FootImageSerializer(footer_images, many=True)

        return Response({'msg': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)




class ProductServiceListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]    
    queryset           = ProductService.objects.all()
    serializer_class   = ProductServiceCRUDSerializer


    def post(self, request):
        user = request.user
        business_id = request.data.get('business_id')
        request.data['business'] = business_id

        serializer = ProductServiceCRUDSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            business_page = Business.objects.get(owner=user)
            if business_page.owner == user:
                serializer.save()
            else:
                return Response({'msg': 'Only Page owner can create Products'})
        except Business.DoesNotExist:
            if user.is_staff:
                serializer.save()
                return Response({'msg': 'Product Created Successfully'}, status=status.HTTP_201_CREATED)
            return Response({"msg": "Not able to Create Product"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'msg': 'Product Created Successfully'}, status=status.HTTP_201_CREATED)





class ProductServiceUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk,*args, **kwargs):
        product_id = request.data.get('product_id')
        user = request.user

        try:
            product = ProductService.objects.get(business=pk, id=product_id)
        except ProductService.DoesNotExist:
            return Response({'msg': 'No Products'})
        
        request.data['business'] = pk

        try:
            business_page = Business.objects.get(id=pk)
            if business_page.owner == user:
                serializer = ProductServiceCRUDSerializer(product, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save() 
            else:
                return Response({'msg': 'Not able to update the Product'})
        except Business.DoesNotExist:
            if user.is_staff:
                serializer = ProductServiceCRUDSerializer(product, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save() 
            else:
                return Response({'msg': 'Not Able to Update Product Data'})

        return Response({'msg': 'Product data updated Successfully'}, status=status.HTTP_200_OK)
    



class ProductServiceDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request,*args, **kwargs):
        user = request.user
        product_id = request.data.get('product_id')
        business_id = request.data.get('business_id')

        try:
            product = ProductService.objects.get(business=business_id, id=product_id)
        except ProductService.DoesNotExist:
            return Response({'msg': 'No Products'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            business_page = Business.objects.get(id=business_id)
            if business_page.owner == user:
                product.delete()
            else:
                return Response({'msg': 'Only Business owner can Delete the product'})
        except Business.DoesNotExist:
            if user.is_staff:
                product.delete()
            else:
                return Response({'msg': 'Not able to delete product'})

        return Response({'msg': 'Product Deleted Successfully'}, status=status.HTTP_200_OK)
    



# class PlanPurchaseAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated,]

#     def post(self, request):
#         serializer = PremiumPlanSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'msg': 'Redirecting to payment page'})
    
from django.db.models import Value
from ADS.models import AdBucket
class LandigPageAdTesting(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        current_user = request.user
        viewed_ad_ids = UserADView.objects.filter(user=current_user, is_viewed=True).values_list('ad', flat=True)
        print(viewed_ad_ids)

        ads = ADS.objects.all().order_by('id').annotate(
                viewed_by_user=Case(
                    When(id__in=viewed_ad_ids, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('viewed_by_user')
        
        return Response({"msg": "Successfull"})
    



class StoreUsersView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        try:
            current_user = request.user
            if current_user.is_authenticated:
                all_ads = request.data.get('ads', [])
                # ad_ids   =  [int(ad_id) for ad_id in str(all_ads)]

                if not isinstance(all_ads, list):
                    return Response({"msg": "Invalid format for 'ads' parameter"}, status=status.HTTP_400_BAD_REQUEST)
                
                for ad_id in all_ads:
                    try:
                        ads = ADS.objects.get(id=ad_id)
                    except ADS.DoesNotExist:
                        return Response({"msg": "Requested Ad does not exist"}, status=status.HTTP_404_NOT_FOUND)
                    
                for ad_id in all_ads:
                    UserADView.objects.create(
                        user      = current_user,
                        ad        = ads.pk,
                        is_viewed = True
                    )
                    ads.views += 1

                    users_ad = AdBucket.objects.get(
                        ad=ads.pk
                        )
                    users_ad.viewed += 1
                    users_ad.assigned_view -= 1

        except ADS.DoesNotExist:
            return Response({"msg": "User is not Authenticated"})

        return Response("Done")
    




class AllBrandsAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class   = PageNumberPagination
    
    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request):
        all_brands = BrandBusinessPage.objects.all()

        all_brand_page = self.paginate_queryset(all_brands)
        serilaizer = BrandBusinessSerializer(all_brand_page, many=True)
        response_data = {
            'all_brands' : serilaizer.data
        }

        return self.get_paginated_response(response_data)