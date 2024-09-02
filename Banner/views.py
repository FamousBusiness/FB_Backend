from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import BannerPaymentSerializer, BannerPaymentCompleteSerializer, BannerUploadSerializer, BannerSerializer
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from .models import Banner
from Listings.models import Order
from ADS.models import ADS
from PremiumPlan.models import UserPremiumPlan, PremiumPlan
from PremiumPlan.serializers import PremiumPlanSerializer
from rest_framework import permissions
from Listings.constants import PaymentStatus
from razorpay.errors import SignatureVerificationError



rz_client = RazorpayClient()



class BannerPremiumPlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        bannerplan = PremiumPlan.objects.filter(type='banner')
        serializer = PremiumPlanSerializer(bannerplan, many=True)
        return Response({'data': serializer.data, 'msg': 'Plans to Post Ad'}, status=status.HTTP_200_OK)
 


class BannerPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = BannerPaymentSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data.get('amount')
            current_user   = request.user
            plan = serializer.validated_data.get('plan')

            razorpay_order = rz_client.create_order(
                amount=amount
            )

            try:
                plan = PremiumPlan.objects.get(id=plan)
            except PremiumPlan.DoesNotExist:
                return Response({'msg': 'Invalid Plan ID'})
            

            provider_order_id = razorpay_order.get("id")
            
            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Order Created',
                'data': razorpay_order,
                
            }  

            order = Order.objects.create(provider_order_id=provider_order_id, amount=amount, plan=plan)
            order.user = current_user
            order.save()

            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class BannerPaymentCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = BannerPaymentCompleteSerializer(request.data)

        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data.get('provider_order_id')
        payment_id = serializer.validated_data.get('payment_id')
        signature_id = serializer.validated_data.get('signature_id')


        try:
            rz_client.verify_payment_signature(
                razorpay_order_id   = order_id,
                razorpay_payment_id = payment_id,
                razorpay_signature  = signature_id
            )
        except SignatureVerificationError as e:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Payment signature verification failed",
                "error": str(e) 
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            order = Order.objects.get(provider_order_id=order_id)
        except Order.DoesNotExist:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Order with the specified provider_order_id not found",
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        

        order.payment_id = payment_id
        order.signature_id = signature_id
        order.isPaid = True
        order.status = PaymentStatus.SUCCESS
        order.save()

        userplan = UserPremiumPlan.objects.get(user=order.user)
        userplan.is_active = True
        

        response = {
            "status_code": status.HTTP_201_CREATED,
            "message": "Transaction created"
        }

        return Response(response, status=status.HTTP_201_CREATED)
    

 
#Upload Banner
class BannerUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BannerUploadSerializer(data=request.data)
        user = request.user
        active_banners = Banner.objects.filter(user=user, expired=False)

        serializer.is_valid(raise_exception=True)

        # if benefits.banner_allowed > benefits.banner_used:
        #     if active_banners:
        #         return Response({'msg': 'You still have active banners'})
        #     serializer.save(user=user)
        #     benefits.banner_used += 1
        #     benefits.save()
        #     return Response({'msg': 'Banner Posted'})
        # elif benefits.banner_allowed == benefits.banner_used:
        #     benefits.banner_allowed = 0
        #     benefits.banner_used = 0
        #     benefits.save()
        # else:
        #     return Response({'msg': 'No banner available please recharge'})
        
        return Response({'msg': 'Data Saved Successfully'}, status=status.HTTP_201_CREATED)

    
    
