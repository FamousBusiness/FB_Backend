from rest_framework.response import Response
from rest_framework import status, permissions
from Listings.models import Category, ProductService, SubCategory
from .models import StoreBanner, ProductTag, Cart, UserAddress, ProductOrders, UserAddress
from Wallet.models import Wallet, Transaction, ImmatureWallet
from Listings.models import Business
from rest_framework import viewsets
from .serializers import (
    StoreHomePageCategorySerializer, StoreHomePageBannerSerializer, CategoryWiseProductSerializer, CartSerializer, 
    ProductServiceSerializer, StoreHomePageProductTagSerializer, CartChecKoutSerializer, UserDeliveryAddressSerializer, MultipleProductSerializer, TotalCartProductQuantitySerializer, ProductOrderSerializer
    )
from .pagination import StoreHomepageProductPagination, StoreCategoryWiseProductViewSetPagination
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from Razorpay.serializer import RazorpayorderSerializer, RazorPayOrderCompletionSerializer
from Razorpay.views import rz_client
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page




CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)





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
        



class CreateProductCartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = Cart.objects.all()
    serializer_class   = CartSerializer


    #### Get all the Carts of user
    def list(self, request, *args, **kwargs):
        """
            Retrieve cart items for the authenticated user
        """
        user       = request.user
        queryset   = Cart.objects.filter(user=user)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
         

    ### Add Cart Item
    def create(self, request, *args, **kwargs):
        user       = request.user
        serializer = self.get_serializer(data=request.data)

        product_id = request.data.get('product')

        ### Check Valid product 
        try:
            product_service = ProductService.objects.get(pk = int(product_id))
        except Exception as e:
            return Response({'message': 'Invalid Product', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer.is_valid(raise_exception = True)

        # product_id = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        cart_item = Cart.objects.filter(
            user    = user,
            product = product_service
        ).first()

        if cart_item:
            cart_item.quantity = quantity
            cart_item.save()

            return Response(
                CartSerializer(cart_item).data,
                status=status.HTTP_200_OK
            )
        
        else:
            cart_item = Cart.objects.create(
                user = user,
                product = product_service,
                quantity = quantity
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    ### Update Cart Item
    def update(self, request, *args, **kwargs):
        user       = request.user
        product_id = request.data.get('product')
        quantity   = request.data.get('quantity')

        ### Check Valid product 
        try:
            product_service = ProductService.objects.get(id = int(product_id))
        except Exception as e:
            return Response({'message': 'Invalid Product'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart_item = Cart.objects.get(user=user, product=product_service)
            cart_item.quantity = quantity
            cart_item.save()

            return Response(
                CartSerializer(cart_item).data,
                status=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart item does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
    
    #### Delete Cart Item
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            {'message': 'Cart item deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
    




class RemoveProductFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user       = request.user
        product_id = request.data.get('product')
        quantity_to_remove = request.data.get('quantity', 0) 

        try:
            product_service = ProductService.objects.get(id=int(product_id))
        except ProductService.DoesNotExist:
            return Response({'message': 'Invalid Product'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the cart item for the user and product
        try:
            cart_item = Cart.objects.get(user=user, product=product_service)
        except Cart.DoesNotExist:
            return Response({'message': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)
        
        if quantity_to_remove >= cart_item.quantity:
            cart_item.delete()
            return Response({'message': 'Product removed from cart'}, status=status.HTTP_204_NO_CONTENT)
        
        cart_item.quantity -= quantity_to_remove
        cart_item.save()


        return Response({
            'message': 'Quantity decreased successfully',
            'product': product_service.name,
            'new_quantity': cart_item.quantity
        }, status=status.HTTP_200_OK)



#### Checkout page 
class CheckoutPageView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = CartChecKoutSerializer

    def get(self, request):
        user = request.user

        if user.is_authenticated:
            user_cart           = Cart.objects.filter(user = user)
            all_user_cart_items = self.serializer_class(user_cart, many=True)

            return Response({
                'message': 'Cart item added successfully',
                'data': all_user_cart_items.data

            }, status=status.HTTP_200_OK)





#### Delivery Address Viewset
class UserDeliveryAddressView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset           = UserAddress.objects.all()
    serializer_class   = UserDeliveryAddressSerializer


    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




#### get multiple products in checkout page
class MultipleProductViewSet(APIView):
    permission_classes = [permissions.AllowAny]


    def post(self, request):
        request_data = request.data['products']

        all_products = []

        for data in request_data:
            product_id = int(data)

            try:
                product_data = ProductService.objects.get(id = product_id)

                all_products.append(product_data)
            except Exception as e:
                pass

        serializer   = MultipleProductSerializer(all_products, many=True)

        return Response({'message': 'Success', 'products': serializer.data}, status=status.HTTP_200_OK)





##### Update Cart and Quantity
class UpdateCartQuantityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user       = request.user
        products   = request.data.get('product')
        quantities = request.data.get('quantity')

        if not products and not quantities:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        # Ensure products and quantities are of the same length
        if len(products) != len(quantities):
            return Response(
                {'message': 'Mismatch between products and quantities'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_data = []

        for product_id, quantity in zip(products, quantities):
            ### Check Valid product 
            try:
                product_service = ProductService.objects.get(pk = int(product_id))
            except Exception as e:
                return Response({'message': 'Invalid Product', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item = Cart.objects.filter(
                user    = user,
                product = product_service
            ).first()

            if cart_item:
                cart_item.quantity += quantity
                cart_item.save()

                response_data.append({'product_id': product_id, 'message': 'Cart updated successfully'})
            
            else:
                cart_item = Cart.objects.create(
                    user = user,
                    product = product_service,
                    quantity = quantity
                )
                response_data.append({'product_id': product_id, 'message': 'Cart created successfully'})

        return Response(response_data, status=status.HTTP_200_OK)
    



#### Get Cart Quantity
class CountCartProdctQuantityView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = TotalCartProductQuantitySerializer

    def get(self, request):
        user = request.user

        quantity = 0

        try:
            user_carts = Cart.objects.filter(user = user)
        except Exception as e:
            return Response({'message': 'Unable fetch user Carts'}, status=status.HTTP_400_BAD_REQUEST)
        
        for cart in user_carts:
            quantity += cart.quantity

        return Response({'quantity': quantity}, status=status.HTTP_200_OK)
    




##### Razorpay Payment Process
class EcomRazorPayPaymentProcess(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):
        razorpay_order_serializer = RazorpayorderSerializer(data = request.data)

        if razorpay_order_serializer.is_valid():
            amount = razorpay_order_serializer.validated_data.get('amount')
            
            order_response = rz_client.create_order(
                amount = amount
            )

            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Order Created',
                'data': order_response
            }

            return Response(response, status=status.HTTP_201_CREATED)

        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": razorpay_order_serializer.errors
            }

            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
    
    ### Handle Payment Success
    def put(self, request):
        currenct_user    = request.user
        order_serializer = RazorPayOrderCompletionSerializer(data = request.data)

        order_serializer.is_valid(raise_exception=True)

        order_id     = order_serializer.validated_data.get('provider_order_id')
        payment_id   = order_serializer.validated_data.get('payment_id')
        signature_id = order_serializer.validated_data.get('signature_id')

        products     = request.data.get('products') 
        address      = request.data.get('address_id')
        
        ### Razorpay payment Varification
        try:
            rz_client.verify_payment_signature(
                razorpay_order_id   = order_id,
                razorpay_payment_id = payment_id,
                razorpay_signature  = signature_id
            )

        except Exception as e:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Payment signature verification failed",
                "error": str(e) 
            }

            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response = {
            "status_code": status.HTTP_201_CREATED,
            "message": "transaction created"
        }


        ### Get the address
        try:
            user_address = UserAddress.objects.get(id = int(address))
        except Exception as e:
            return Response({'message': 'Unable to get the address'}, status=status.HTTP_400_BAD_REQUEST)
        

        ### Assign the product and Quantity to the user and Business
        for product_data in products:
            product_id = product_data.get('product_id')
            quantity   = product_data.get('quantity')

            ### Get the product
            try:
                product = ProductService.objects.get(id = int(product_id))
            except Exception as e:
                return Response({'message': 'Unable to get the product'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            ### Create an Ecommerce Order
            ecom_order = ProductOrders.objects.create(
                user     = currenct_user,
                business = product.business,
                product  = product,
                quantity = quantity,
                is_paid  = True,
                address  = user_address,
                order_placed_at = timezone.now(),
                order_placed = True
            )

            ### Get the Business user
            try:
                business_user = Business.objects.get(owner = product.business.owner)
            except Exception as e:
                return Response({'message': 'Unable to get the Business'}, status=status.HTTP_400_BAD_REQUEST)
            
            ### Create or get the Business user Wallet
            try:
                wallet, created = ImmatureWallet.objects.get_or_create(
                    user = business_user.owner
                )

                if wallet:
                    wallet.balance += float(product.price)
                    wallet.save()

            except Exception as e:
                return Response({'message': 'Not able to get the Wallet'}, status=status.HTTP_400_BAD_REQUEST)

            ecom_order.save()

        return Response(response, status=status.HTTP_201_CREATED)



    


#### Get all the available orders of the Business
class AllBusinessOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get(self, request):
        user = request.user
        
        try:
            business = Business.objects.get(owner = user)

            if business:
                try:
                    business_orders = ProductOrders.objects.filter(business = business)
                except Exception as e:
                    return Response({'message': 'Unable to get the orders', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = ProductOrderSerializer(business_orders, many=True)

                return Response({
                    'all_users_orders': serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            try:
                user_orders = ProductOrders.objects.filter(user = user)
            except Exception as e:
                return Response({'message': 'Unable to get the orders', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = ProductOrderSerializer(user_orders, many=True)

            return Response({'all_user_orders': serializer.data}, status=status.HTTP_200_OK)
            


