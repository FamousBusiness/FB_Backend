from Listings.models import Category, ProductService
from rest_framework import serializers
from .models import StoreBanner, ProductOffers, ProductSpecification, ProductTag, ProductImages


### Categories visible at the top bar on store homepage
class StoreHomePageCategorySerializer(serializers.ModelSerializer):
    subcategory_names = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'type', 'B2B2C', 'image', 'trending', 'is_store', 'subcategory_names']

    def get_subcategory_names(self, obj):
        return list(obj.subcategory_set.values_list('name', flat=True))


### Banner serializer on store Home page
class StoreHomePageBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreBanner
        fields = "__all__"


### Store Home page product
class StoreHomePageProductSerializer(serializers.ModelSerializer):
    product_tag_name = serializers.CharField(source='product_tag.name', read_only = True)

    class Meta:
        model = ProductService
        fields = ['id', 'name', 'picture', 'price', 'description', 'product_tag', 'product_tag_name']


### Home page Tags
class StoreHomePageProductTagSerializer(serializers.ModelSerializer):
    products = StoreHomePageProductSerializer(source='productservice_set', many=True, read_only=True)

    class Meta:
        model = ProductTag
        fields = ['id', 'name', 'products']



#### Products On Category wise store page
class CategoryWiseProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductService
        fields = ['id', 'name', 'picture', 'price', 'description', 'category', 'subcategory', 'rating', 'discount_price', 'percentage_off', 'is_sponsored', 'reviews']



### Product offers
class ProductOfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductOffers
        fields = "__all__"


### Product Specifications Serializer
class ProductSpecificationsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductSpecification
        fields = "__all__"


### Product Images
class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImages
        fields = "__all__"


### Product page
class ProductServiceSerializer(serializers.ModelSerializer):
    offers        = ProductOfferSerializer(many=True, read_only=True)
    specification = ProductSpecificationsSerializer(many=True, read_only=True)
    multiple_img  = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductService
        fields = [
            'id', 'name', 'picture', 'price', 'description', 'description2', 'category', 'subcategory', 'rating','reviews', 'discount_price', 'percentage_off', 'emi_amount', 'is_available',
            'offers', 'specification', 'multiple_img', 'is_sponsored', 'reviews'
        ]
