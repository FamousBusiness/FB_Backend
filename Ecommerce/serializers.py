from Listings.models import Category, ProductService
from rest_framework import serializers
from .models import StoreBanner, ProductOffers, ProductSpecification, ProductTag, ProductImages, Cart, UserAddress, ProductOrders, EMIOffers
from Listings.models import BrandBusinessPage, Business
from users.models import User



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


class EMIOfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = EMIOffers
        fields = '__all__'


class BrandNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrandBusinessPage
        fields = ['brand_name']



### Product page
class ProductServiceSerializer(serializers.ModelSerializer):
    offers        = ProductOfferSerializer(many=True, read_only=True)
    specification = ProductSpecificationsSerializer(many=True, read_only=True)
    multiple_img  = ProductImageSerializer(many=True, read_only=True)
    emi_offers    = EMIOfferSerializer(many=True, read_only=True)
    brand         = BrandNameSerializer()

    class Meta:
        model = ProductService
        fields = [
            'id', 'name', 'picture', 'price', 'description', 'description2', 'category', 'subcategory', 'rating','reviews', 'discount_price', 'percentage_off', 'emi_amount', 'is_available',
            'offers', 'specification', 'multiple_img', 'is_sponsored', 'reviews', 'emi_offers', 'brand'
        ]



#### Cart Serializer
class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = ['product', 'quantity']




#### Checkout page serializer
class CartChecKoutSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'quantity', 'product_details']
    
    
    def get_product_details(self, obj):
        try:
            product = ProductService.objects.get(id=obj.product.id)
            return ProductServiceSerializer(product).data
        except Exception as e:
            return None
        



#### User delivery Address Serializer
class UserDeliveryAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model  = UserAddress
        fields = '__all__'
        read_only_fields = ['user']



#### Multiple product serializer
class MultipleProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductService
        fields = [
            'id', 'name', 'picture', 'price', 'description', 'description2', 'category', 'subcategory', 'rating','reviews', 'discount_price', 'percentage_off', 'emi_amount', 'is_available', 'is_sponsored', 'reviews'
        ]


#### Total Cart Quantity Serializer
class TotalCartProductQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()



#### Used in Order detail Serializer
class BusinessNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ['business_name']



class UserNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name']



### Product Service Serializer for User and Business orders(To avoid sending all data)
class ProductServiceOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductService
        fields = [
            'business', 'name', 'picture', 'price', 'description', 'product_tag', 'rating', 'reviews', 'discount_price', 'percentage_off', 'emi_amount', 'offers'
            ]



#### User in Order details serializer
class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAddress
        fields = '__all__'


### All Orders
class ProductOrderSerializer(serializers.ModelSerializer):
    product  = ProductServiceOrderSerializer()

    class Meta:
        model = ProductOrders
        fields = [
            'id', 'user', 'business', 'product', 'quantity', 'is_paid', 'address', 'order_placed', 'order_placed_at', 'shipped_at', 'is_shipped', 'out_of_delivery', 'out_of_delivery_at', 'is_delivered', 'delivered_at', 'order_id'
        ]
        



#### Specific order serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    product  = ProductServiceOrderSerializer()
    address  = OrderSerializer()
    business = BusinessNameSerializer()
    user     = UserNameSerializer()


    class Meta:
        model = ProductOrders
        fields = [
            'id', 'user', 'business', 'product', 'quantity', 'is_paid', 'address', 'order_placed', 'order_placed_at', 'shipped_at', 'is_shipped', 'out_of_delivery', 'out_of_delivery_at', 'is_delivered', 'delivered_at', 'order_id', 'status', 'order_confirmed', 'order_confirmed_at'
        ]





    
