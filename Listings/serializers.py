from rest_framework import serializers
from Listings.models import (
    Business, BusinessMobileNumbers, BusinessImage,
    Category,Order, ProductService, FooterImage,
    FrontCarousel, BusinessPageLike, LocalBusinessSchemaInstagram,LocalBusinessSchemaAggregrateRating, LocalBusinessSchemaVideo, LocalBusinessSchemaFaceBook,LocalSchemaVideoInteractionStatitics,
    BusinessPageReviewRating, Image, LocalSchemaSameAs,CategoryWiseBusinessSideImage, LocalSchemaSearchKeywords, LocalSchemaFacebookInteractionStatitics, LocalSchemaInstagramInteractionStatitics, LocalBusinessSchemaReviews, FAQSchemaMainEntity, BreadCrumbSchamaItemListItem, ArticleSchema
)
from Banner.models import Banner
from Brands.models import BrandProducts, BrandBusinessPage
from Lead.models import Lead
from users.models import User


#Images will be sent According to the location and category of the banner
class CategoryWiseBusinessSideImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CategoryWiseBusinessSideImage
        fields = ['image1', 'image2']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image1:
            image1_path = f"https://mdwebzotica.famousbusiness.in/{instance.image1.name}"
            representation["image1"] = image1_path

        if instance.image2:
            image2_path = f"https://mdwebzotica.famousbusiness.in/{instance.image2.name}"
            representation['image2'] = image2_path

        return representation
    
    
#Linked to()     
class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path

        return representation



class IDWiseBusinessImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Image
        fields = '__all__'  

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path

        return representation


#USed in (IDWise Business, Category wise business)
class BusinessImageSerializer(serializers.ModelSerializer):
    images = IDWiseBusinessImageSerializer(many=True, read_only=True)

    class Meta:
        model  = BusinessImage
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        business_id = instance.business.id
        images = Image.objects.filter(businessimage__business_id=business_id)
        images_data = IDWiseBusinessImageSerializer(images, many=True).data

        if instance.image:
            representation['image'] = images_data

        return representation
    
  

class OrderSerializer(serializers.ModelSerializer):
    order_date = serializers.DateTimeField(format="%d %B %Y %I:%M %p")

    class Meta:
        model = Order
        fields = '__all__'
#         # depth = 2


class SingleListingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['business_name', 'mobile_number', 'email', 'website_url', 'business_info',]

        business_name = serializers.CharField(required=True)
        website_url = serializers.CharField(required=True)
        business_info = serializers.CharField(required=True)    





class BannerSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    # side_images = CategoryWiseBusinessSideImageSerializer(many=True, read_only=True, source='category.categywisebannersideimages')

    class Meta:
        model = Banner
        fields = ['id','category', 'image', 'state', 'city', 'verified', 'expired', 'created_on']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path

        return representation



class FrontCarouselSerializer(serializers.ModelSerializer):

    class Meta:
        model = FrontCarousel
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            # image_path   = instance.image.url
            representation['image'] = image_path
        else:
            representation['image'] = None

        if instance.video:
            video_path = f"https://mdwebzotica.famousbusiness.in/{instance.video.name}"
            # video_path   = instance.video.url
            representation['video'] = video_path
        else:
            representation['video'] = None

        return representation
    


class SearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business



class LandingPageBrandProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandProducts
        fields = ['brand', 'name', 'price', 'image', 'description']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path
        else:
            representation['image'] = None

        return representation


class LandingPageBrandSerializer(serializers.ModelSerializer):
    products = LandingPageBrandProductSerializer(source='brandproducts_set',  many=True, read_only=True)

    class Meta:
        model = BrandBusinessPage
        fields = ['id', 'brand_name' ,'icons', 'products']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        if instance.icons:
            icon_path = f"https://mdwebzotica.famousbusiness.in/{instance.icons.name}"
            representation['icons'] = icon_path
        else:
            representation['icons'] = None

        return representation



class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'mobile_number', 'email', 'location']





class CategoryLeadGenerateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = ['category']


class BusinessMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessMobileNumbers
        fields = ['mobile_number']


class CategorywiseBusinessSerilizer(serializers.ModelSerializer):
    picture = serializers.ImageField()
    mobile_numbers = BusinessMobileSerializer(source='businessmobilenumbers_set', many=True, read_only=True)
    business_images = BusinessImageSerializer(source='businessimage_set', many=True, read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'business_name', 'mobile_numbers','state','city','pincode','whatsapp_number','email','website_url','GSTIN','business_info',
                  'established_on', 'services','verified','trusted','trending','authorized','picture','likes','reviews', 'mobile_number',
                  'category', 'business_images', 'industry_leader', 'sponsor', 'super', 'premium'
                  ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.picture:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
            representation['picture'] = image_path

        return representation

    # def get_mobile_numbers(self, obj):
    #     # Retrieve the related mobile numbers for the current Business instance
    #     mobile_numbers_queryset = BusinessMobileNumbers.objects.filter(business=obj)
    #     mobile_numbers_serializer = BusinessMobileSerializer(mobile_numbers_queryset, many=True)
    #     return mobile_numbers_serializer.data

        

class ProductServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model  = ProductService
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.picture:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
            representation['picture'] = image_path

        return representation


class BusinessPageLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPageLike
        fields = '__all__'

class OnlyUserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name']


class OnlyBusinessNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['business_name']


#Used in Profile Page
class BusinessPageReviewRatingSerializer(serializers.ModelSerializer):
    # user_name     = serializers.SerializerMethodField()
    # business_name = serializers.SerializerMethodField()

    def get_user_name(sellf, obj):
        user_id         = obj.user.id
        name            = User.objects.filter(id = user_id)
        name_serializer = OnlyUserNameSerializer(name, many=True).data
        return name_serializer
    
    def get_business_name(sellf, obj):
        business_id              = obj.business_page.id
        business_name            = Business.objects.filter(id = business_id)
        business_name_serializer = OnlyBusinessNameSerializer(business_name, many=True).data
        return business_name_serializer
    
    class Meta:
        model = BusinessPageReviewRating
        fields = ['rating', 'review', 'user', 'business_page']


#### User name serializer
class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name']


##### SEO Serializers
class LocalSchemaSearchKeywordsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalSchemaSearchKeywords
        fields = '__all__'


class LocalSchemaSameAsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalSchemaSameAs
        fields = '__all__'


class LocalBusinessSchemaAggregrateRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalBusinessSchemaAggregrateRating
        fields = '__all__'


class LocalSchemaVideoInteractionStatiticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalSchemaVideoInteractionStatitics
        fields = '__all__'



class LocalBusinessSchemaVideoSerializer(serializers.ModelSerializer):
    interactionStatistic = LocalSchemaVideoInteractionStatiticsSerializer(many=True)

    class Meta:
        model = LocalBusinessSchemaVideo
        fields = '__all__'



class LocalSchemaFacebookInteractionStatiticsSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocalSchemaFacebookInteractionStatitics
        fields = '__all__'



class LocalBusinessSchemaFaceBookSerializer(serializers.ModelSerializer):
    interactionStatistic = LocalSchemaFacebookInteractionStatiticsSerializer(many=True)

    class Meta:
        model = LocalBusinessSchemaFaceBook
        fields = '__all__'



class LocalSchemaInstagramInteractionStatiticsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = LocalSchemaInstagramInteractionStatitics
        fields = '__all__'



class LocalBusinessSchemaInstagramSerializer(serializers.ModelSerializer):
    interactionStatistic = LocalSchemaInstagramInteractionStatiticsSerializer(many = True)

    class Meta:
        model = LocalBusinessSchemaInstagram
        fields = '__all__'



class LocalBusinessSchemaReviewsSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()

    class Meta:
        model = LocalBusinessSchemaReviews
        fields = '__all__'



class FAQSchemaMainEntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = FAQSchemaMainEntity
        fields = '__all__'



class BreadCrumbSchamaItemListItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = BreadCrumbSchamaItemListItem
        fields = '__all__'



class ArticleSchemaSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()

    class Meta:
        model = ArticleSchema
        fields = '__all__'



class IDwiseBusinessSerilizer(serializers.ModelSerializer):
    picture         = serializers.ImageField()
    business_images = BusinessImageSerializer(source='businessimage_set', many=True, read_only=True)
    products        = ProductServiceSerializer(source='productservice_set', many=True, read_only=True)
    mobile_numbers  = BusinessMobileSerializer(source='businessmobilenumbers_set', many=True, read_only=True)
    like            = serializers.SerializerMethodField()
    ReviewRatings   = serializers.SerializerMethodField()
    category        = CategorySerializer()
    local_schema_search_keyword    = LocalSchemaSearchKeywordsSerializer(many=True)
    local_schema_same_as           = LocalSchemaSameAsSerializer(many = True)
    local_schema_aggregrate_rating = LocalBusinessSchemaAggregrateRatingSerializer()
    local_schema_video             = LocalBusinessSchemaVideoSerializer()
    local_schema_facebook_video    = LocalBusinessSchemaFaceBookSerializer()
    local_schema_insta_video       = LocalBusinessSchemaInstagramSerializer()
    local_schema_reviews           = LocalBusinessSchemaReviewsSerializer(many=True)
    faq_schema_mainEntity          = FAQSchemaMainEntitySerializer(many=True)
    brad_crumb_schema_item_list    = BreadCrumbSchamaItemListItemSerializer(many=True)
    article_schema                 = ArticleSchemaSerializer()


    def get_like(self, obj):
        business_id = obj.id
        like_count = BusinessPageLike.objects.filter(business_page_id=business_id).count()
        return like_count
    
    def get_ReviewRatings(self, obj):
        business_id = obj.id
        reviewrating = BusinessPageReviewRating.objects.filter(business_page_id=business_id)
        serialized_ratings = BusinessPageReviewRatingSerializer(reviewrating, many=True).data
        return serialized_ratings
    
    class Meta:
        model = Business
        fields = [
                 'id', 'business_name','state','city','pincode','whatsapp_number','email','website_url','GSTIN','business_info',
                  'established_on', 'services','verified','trusted','trending','authorized','picture','like','reviews', 'mobile_number',
                  'address', 'business_images', 'products', 'mobile_numbers','nature', 'opening_time','closing_time','turn_over',
                  'employee_count', 'category', 'ReviewRatings', 'CIN_No', 'DIN', 'director', 'RoC', 'company_No', 'industry_leader',
                  'sponsor', 'super', 'premium', 'locality', 'local_schema_search_keyword', 'local_schema_same_as', 'local_schema_aggregrate_rating', 'local_schema_video', 'local_schema_facebook_video', 'local_schema_insta_video', 'local_schema_reviews', 'faq_schema_mainEntity', 'brad_crumb_schema_item_list', 'article_schema'
                ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.picture:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
            representation['picture'] = image_path
    
        return representation


class FootImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = FooterImage
        fields = ['image', 'image2', 'description']


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path

        return representation
    

class UserSpecificBusinessPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['business_name', 'business_info', 'category', 'website_url', 'city', 'state', 'pincode', 'address', 'employee_count',
                  'turn_over', 'nature', 'opening_time', 'closing_time', 'keywords', 'services', 'established_on', 'director', 'RoC',
                  'company_No', 'DIN', 'CIN_No', 'GSTIN', 'mobile_number', 'whatsapp_number', 'email']



class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']


# class BusinessImageUpdateSerializer(serializers.ModelSerializer):
#     images = ImageSerializer(many=True)

#     class Meta:
#         model = BusinessImage
#         fields = '__all__'

#     def create(self, validated_data):
#         images_data = validated_data.pop('image')
#         business_image = BusinessImage.objects.create(**validated_data)

#         for image_data in images_data:
#             image = Image.objects.create(**image_data)
#             business_image.image.add(image)

#         return business_image

#     def update(self, instance, validated_data):
#         images_data = validated_data.pop('image')
#         instance.business = validated_data.get('business', instance.business)
#         instance.save()

#         instance.image.clear()
#         for image_data in images_data:
#             image = Image.objects.create(**image_data)
#             instance.image.add(image)

#         return instance
    

class ProductServiceCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductService
        fields = [ 'business', 'name', 'picture', 'price', 'description']




class BusinessSerializer(serializers.ModelSerializer):
    picture         = serializers.ImageField()
    business_images = BusinessImageSerializer(source='businessimage_set', many=True, read_only=True)
    mobile_numbers  = BusinessMobileSerializer(source='businessmobilenumbers_set', many=True, read_only=True)
    ReviewRatings   = serializers.SerializerMethodField()

    def get_like(self, obj):
        business_id = obj.id
        like_count = BusinessPageLike.objects.filter(business_page_id=business_id).count()
        return like_count
    
    def get_ReviewRatings(self, obj):
        business_id = obj.id
        reviewrating = BusinessPageReviewRating.objects.filter(business_page_id=business_id)
        serialized_ratings = BusinessPageReviewRatingSerializer(reviewrating, many=True).data
        return serialized_ratings
    

    class Meta:
        model = Business
        fields = [
                 'id', 'business_name','state','city','pincode','whatsapp_number','email','website_url','GSTIN','business_info',
                  'established_on', 'services','verified','trusted','trending','authorized','picture', 'mobile_number',
                  'address', 'business_images', 'mobile_numbers','nature', 'opening_time','closing_time','turn_over',
                  'employee_count', 'category', 'likes', 'ReviewRatings', 'CIN_No', 'DIN', 'director', 'RoC', 'company_No', 'industry_leader',
                  'sponsor', 'super', 'premium'
                  ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.picture:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
            representation['picture'] = image_path

        return representation
    



class BrandBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandBusinessPage
        fields = "__all__"

    
    
    

