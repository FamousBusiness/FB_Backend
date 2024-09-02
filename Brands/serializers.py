from rest_framework import serializers
from .models import BrandBusinessPage, BrandProducts
from Listings.models import Business



class BrandBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandBusinessPage
        fields = "__all__"



#Used in Laanding Page and Brand Profile Page
class BrandProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandProducts
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        if instance.image:
            image_path = f"https://mdwebzotica.famousbusiness.in/{instance.image.name}"
            representation['image'] = image_path
        else:
            representation['image'] = None

        return representation


    
#Used in Landing Page
class BrandSerializer(serializers.ModelSerializer):
    products = BrandProductSerializer(source='brandproducts_set',  many=True, read_only=True)

    class Meta:
        model = BrandBusinessPage
        fields = ['id', 'icons', 'products']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        if instance.icons:
            icon_path = f"https://mdwebzotica.famousbusiness.in/{instance.icons.name}"
            representation['icons'] = icon_path
        else:
            representation['icons'] = None

        return representation
    


class BrandProductCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BrandProducts
        fields = [ 'brand', 'name', 'image', 'price', 'description']




class BrandProfilePageSerializer(serializers.ModelSerializer):
    # business_images = BusinessImageSerializer(source='businessimage_set', many=True, read_only=True)
    # mobile_numbers  = BusinessMobileSerializer(source='businessmobilenumbers_set', many=True, read_only=True)
    # like            = serializers.SerializerMethodField()
    # ReviewRatings   = serializers.SerializerMethodField()
    # picture         = serializers.ImageField()
    products        = BrandProductSerializer(source='brandproducts_set', many=True, read_only=True)


    # def get_like(self, obj):
    #     business_id = obj.id
    #     like_count = BusinessPageLike.objects.filter(business_page_id=business_id).count()
    #     return like_count
    
    # def get_ReviewRatings(self, obj):
    #     business_id = obj.id
    #     reviewrating = BusinessPageReviewRating.objects.filter(business_page_id=business_id)
    #     serialized_ratings = BusinessPageReviewRatingSerializer(reviewrating, many=True).data
    #     return serialized_ratings
    
    class Meta:
        model = BrandBusinessPage
        fields = [
                 'id', 'owner', 'brand_name', 'business_name', 'category', 'email', 'mobile_number', 'whatsapp_number',
                 'GSTN', 'CIN_No', 'DIN', 'RoC', 'company_No', 'director', 'address', 'about', 'web_url', 'turn_over',
                 'employee_count', 'verified', 'trusted', 'trending', 'authorized', 'establishment', 'nature', 'service',
                 'icons', 'industry_leader', 'sponsor', 'super', 'premium', 'opening_time', 'closing_time', 'products'
                  ]

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)

    #     if instance.picture:
    #         image_path = f"https://mdwebzotica.famousbusiness.in/{instance.picture.name}"
    #         representation['picture'] = image_path
    
    #     return representation