from rest_framework.response import Response
from rest_framework import status, permissions
from Listings.models import Category, ProductService, SubCategory
from .models import StoreBanner, ProductTag, Cart, UserAddress, ProductOrders, UserAddress, EcommercePhonepeOrder, RefundTransaction
from Wallet.models import ImmatureWallet
from Listings.models import Business
from rest_framework import viewsets
from .serializers import (
    StoreHomePageCategorySerializer, StoreHomePageBannerSerializer, CategoryWiseProductSerializer, CartSerializer, 
    ProductServiceSerializer, StoreHomePageProductTagSerializer, CartChecKoutSerializer, UserDeliveryAddressSerializer, MultipleProductSerializer, TotalCartProductQuantitySerializer, ProductOrderSerializer, OrderDetailSerializer
    )
from .pagination import StoreHomepageProductPagination, StoreCategoryWiseProductViewSetPagination
from .generateID import generate_orderID
from rest_framework.views import APIView
from Razorpay.serializer import RazorpayorderSerializer, RazorPayOrderCompletionSerializer
from Razorpay.views import rz_client
from django.utils import timezone
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from Phonepe.payment import PhonepayPayment
from django.views.decorators.csrf import csrf_exempt
from Phonepe.encoded import base64_decode
import uuid
import json






CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)





#### Categories at the top of the Store Home page
class StoreCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StoreHomePageCategorySerializer

    def get_queryset(self):
        return Category.objects.filter(
            is_store       = True,
            store_trending = True
            )[:9]
    



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
        # subcategory_name = self.request.query_params.get("subcategory")

        if not category_id:
            return Response({"error": "category_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = ProductService.objects.all()

        queryset = queryset.filter(category_id=category_id)

        # if subcategory_name:
        #     try:
        #         subcategory = SubCategory.objects.get(name=subcategory_name)
        #         queryset = queryset.filter(subcategory=subcategory)
        #     except ObjectDoesNotExist:
        #         return Response({"error": f"SubCategory with name '{subcategory_name}' does not exist."},status=status.HTTP_404_NOT_FOUND)

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

            total_amount = sum(float(cart_item.product.price) * float(cart_item.quantity) for cart_item in user_cart)
            
            return Response({
                'message': 'Cart item added successfully',
                'data': all_user_cart_items.data,
                'totalAmount': total_amount

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
        user     = request.user
        data     = request.data
        amount   = request.data.get('amount')
        products = request.data.get('products')
        address  = request.data.get('address_id')

        phonepe_amount = int(amount) * 100

        required_fields = ['amount', 'products', 'address_id']

        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'message': f'{field} field is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        transaction_id = str(uuid.uuid4())[:35]

        ### Get the address
        try:
            user_address = UserAddress.objects.get(id = int(address))
        except Exception as e:
            return Response({'message': 'Unable to get the address'}, status=status.HTTP_404_NOT_FOUND)

        # Create Phonepe Order
        try:
            phonepe_order = EcommercePhonepeOrder.objects.create(
                user           = user,
                transaction_id = transaction_id,
                address        = user_address,
                products       = str(products),
                amount         = int(amount),
            )
            phonepe_order.save()

        except Exception as e:
            return Response({'message': 'Unable to create Phonepe Order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            payment  = PhonepayPayment(int(amount), transaction_id)
        except Exception as e:
            return Response({'message': 'Unable to raise payment request', 'error': f'{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Payment request raised successfully',
            'url': payment
        }, status=status.HTTP_200_OK)
    
    
    
    ### Handle Payment Success from Razorpay
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

            #### Generate Unique Order ID
            generate_order_id = generate_orderID()

            ### Get the product
            try:
                product = ProductService.objects.get(id = int(product_id))
            except Exception as e:
                return Response({'message': 'Unable to get the product'}, status=status.HTTP_400_BAD_REQUEST)
            
            
            ### Create an Ecommerce Order
            ecom_order = ProductOrders.objects.create(
                user            = currenct_user,
                business        = product.business,
                product         = product,
                quantity        = quantity,
                is_paid         = True,
                address         = user_address,
                order_placed_at = timezone.now(),
                order_placed    = True,
                order_id        = generate_order_id,
                status          = 'Order Placed'
            )

            ecom_order.save()

            #### Delete all the cart items of the user
            try:
                all_user_cart = Cart.objects.filter(user = currenct_user)

                all_user_cart.delete()
            except Exception as e:
                return Response({"message": "No available items in user cart"}, status=status.HTTP_400_BAD_REQUEST)
            

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
            

        return Response(response, status=status.HTTP_201_CREATED)




##### Phonepe Payment Response
class EcomPhonepePaymentResponseView(APIView):
    permission_classes = [permissions.AllowAny]
    
     
    @csrf_exempt
    def post(self, request):
        response_data = request.data.get('response')
        decoded_data = base64_decode(response_data)


        if (
            decoded_data['success'] == True and 
            decoded_data['code'] == 'PAYMENT_SUCCESS' and 
            decoded_data['message'] == 'Your request has been successfully completed.'
            ):

            #### Get the transaction ID from response
            transaction_id = decoded_data['data']['merchantTransactionId']

            #### Get the Phonepe order for the transaction id
            try:
                ecom_phonepe_order = EcommercePhonepeOrder.objects.get(transaction_id = transaction_id)
                ecom_phonepe_order.response = str(decoded_data)

                ecom_phonepe_order.save()
            except Exception as e:
                return Response({'success': True}, status=status.HTTP_200_OK)
            
            ### Get the address and products form phonepe order
            address  = ecom_phonepe_order.address


            try:
                fixed_products = ecom_phonepe_order.products.replace("'", '"')
                products = json.loads(fixed_products)
            except Exception as e:
                return Response({'message': 'Unable to decode Json'}, status=status.HTTP_400_BAD_REQUEST)
            

            for product_data in products:
                product_id = product_data.get('product_id')
                quantity   = product_data.get('quantity')

                #### Generate Unique Order ID
                generate_order_id = generate_orderID()

                
                ### Get the product
                try:
                    product = ProductService.objects.get(id = int(product_id))
                except Exception as e:
                    return Response({'message': 'Unable to get the product'}, status=status.HTTP_400_BAD_REQUEST)
                

                try:
                    ### Create an Ecommerce Order
                    ecom_order = ProductOrders.objects.create(
                        user            = ecom_phonepe_order.user,
                        business        = product.business,
                        product         = product,
                        quantity        = quantity,
                        is_paid         = True,
                        address         = address,
                        order_placed_at = timezone.now(),
                        order_placed    = True,
                        order_id        = generate_order_id,
                        status          = 'Order Placed'
                    )

                    ecom_order.save()

                except Exception as e:
                    return Response({'message': 'Unable to create Order'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                

                #### Delete all the cart items of the user
                try:
                    all_user_cart = Cart.objects.filter(user = ecom_phonepe_order.user)

                    all_user_cart.delete()
                except Exception as e:
                    return Response({"message": "No available items in user cart"}, status=status.HTTP_400_BAD_REQUEST)
                

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
                

            return Response({'success': True}, status=status.HTTP_201_CREATED)
    



#### Get all the available orders of the user's
class AllUserOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            user_orders = ProductOrders.objects.filter(user = user)
        except Exception as e:
            return Response({'message': 'Unable to get the orders', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductOrderSerializer(user_orders, many=True)

        return Response({'all_user_orders': serializer.data}, status=status.HTTP_200_OK)



#### Get all the available orders of the user's
class AllBusinessOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    
    def get(self, request):
        user = request.user
        
        try:
            business_page = Business.objects.get(owner = user)
        except Exception as e:
            return Response({'all_user_orders': []}, status=status.HTTP_200_OK)
        
        try:
            business_orders = ProductOrders.objects.filter(business = business_page)
        except Exception as e:
            return Response({'message': 'Unable to get the orders', 'error': f"{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductOrderSerializer(business_orders, many=True)
    
        return Response({'all_business_orders': serializer.data}, status=status.HTTP_200_OK)




#### All Store Categories
class AllStoreCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StoreHomePageCategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Category.objects.filter(is_store = True)
    




#### Check Product Pincode 
class CheckProductAvailabilityView(APIView):
    permission_classes = [permissions.AllowAny]

    
    def get(self, request): 
        product_id = request.query_params.get('product_id')
        pincode    = request.query_params.get('pincode')

        #### Get the product 
        try:
            product = ProductService.objects.get(id = int(product_id))
        except Exception as e:
            return Response({
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        pincodes = product.pincode.all()

        for pin in pincodes:
            
            if pincode == pin.name:
                return Response({
                    'success': True
                }, status=status.HTTP_200_OK)

        return Response({
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)




#### Get details of a specific order
class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = OrderDetailSerializer


    def get(self, request):
        user = request.user
        order_id = request.query_params.get('order_id')

        if not order_id:
            return Response({'message': 'Please provide order id'}, status=status.HTTP_400_BAD_REQUEST)
        

        ##### Get the order of the user
        try:
            user_order = ProductOrders.objects.get(id = int(order_id))
        except Exception as e:
            return Response({'message': 'Unable to get user order'}, status=status.HTTP_400_BAD_REQUEST)
        
        serilaizer = self.serializer_class(user_order)

        return Response({
            'message': 'order details fetched successfully',
            'order_detail': serilaizer.data

        }, status=status.HTTP_200_OK)




##### Update order status
class UpdateOrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]


    def put(self, request):
        user = request.user

        request_status = request.data.get('status')
        order_id       = request.data.get('order_id')

        if not request_status:
            return Response({'message': 'staus field required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not order_id:
            return Response({'message': 'order_id field required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = ProductOrders.objects.get(id = int(order_id))
        except Exception as e:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        
        if request_status == 'Order Confirmed':
            if (
                order.order_placed
                and not order.order_confirmed
                and not order.is_shipped
                and not order.out_of_delivery
                and not order.is_delivered 
                and not order.is_refundInitiated 
                and not order.is_refunded 
                and not order.is_return_initiated
                and not order.is_returned
                ):
                order.order_confirmed    = True
                order.order_confirmed_at = timezone.now()
                order.status             = 'Order Confirmed'

            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        elif request_status == 'Shipped':
            if (
                order.order_placed 
                and order.order_confirmed
                and not order.is_shipped
                and not order.out_of_delivery
                and not order.is_delivered 
                and not order.is_refundInitiated 
                and not order.is_refunded 
                and not order.is_return_initiated
                and not order.is_returned
                ):

                order.is_shipped = True
                order.shipped_at = timezone.now()
                order.status     = 'Shipped'

            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        elif request_status == 'Out of Delivery':
            if (
                order.order_placed 
                and order.order_confirmed 
                and order.is_shipped
                and not order.out_of_delivery
                and not order.is_delivered 
                and not order.is_refundInitiated 
                and not order.is_refunded 
                and not order.is_return_initiated
                and not order.is_returned
                ):
                order.out_of_delivery = True
                order.out_of_delivery_at = timezone.now()
                order.status = 'Out of Delivery'

            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)
        

        elif request_status == 'Delivered':
            if (
                order.order_placed 
                and order.order_confirmed 
                and order.is_shipped 
                and order.out_of_delivery
                and not order.is_delivered 
                and not order.is_refundInitiated 
                and not order.is_refunded 
                and not order.is_return_initiated
                and not order.is_returned
                ):

                order.is_delivered = True
                order.delivered_at = timezone.now()
                order.status = 'Delivered'

            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request_status == 'Return Shipped':
            if (
                order.order_placed 
                and order.order_confirmed
                and order.is_shipped
                and order.out_of_delivery
                and order.is_delivered
                and order.is_return_initiated
                and not order.is_returned
                and not order.is_refundInitiated
                and not order.is_refunded
            ):
                order.is_return_initiated = True
                order.return_initiate_at  = timezone.now()
                order.status = 'Return Shipped'

            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)
            
        
        elif request_status == 'Returned':
            if (
                order.order_placed
                and order.order_confirmed
                and order.is_shipped
                and order.out_of_delivery
                and order.is_delivered
                and order.is_return_initiated
                and not order.is_returned
                and not order.is_refundInitiated
                and not order.is_refunded
                ):

                order.is_returned        = True
                order.is_refundInitiated = True
                order.returned_at        = timezone.now()
                order.refund_initiate_at = timezone.now()
                order.status             = 'Refund Initiated'

                unique_id = str(uuid.uuid4())[:36]
                
                #### Create a Refund Transaction
                try:
                    refund_transaction = RefundTransaction.objects.create(
                        user         = order.user,
                        business     = order.business,
                        order        = order,
                        reference_id = unique_id,
                        is_refunded  = False,
                        status       = 'Initiated'
                    )

                    refund_transaction.save()
                    
                except Exception as e:
                    return Response({'message': 'Unable to create Refund Transaction'}, status=status.HTTP_400_BAD_REQUEST)
                
            else:
                return Response({'message': 'Unable to change the status'}, status=status.HTTP_400_BAD_REQUEST)

            
        elif request_status == 'Cancelled':
            if order.order_placed and order.order_confirmed:
                order.is_cancelled = True
                order.cancelled_at = timezone.now()

        else:
            return Response({'message': 'invalid status to update'}, status=status.HTTP_400_BAD_REQUEST)

        order.save()
        
        return Response({'success': True}, status=status.HTTP_200_OK)



    






        
