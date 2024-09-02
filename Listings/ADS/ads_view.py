from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .ads_serializers import ADPaymentSerializer, ADPaymentCompleteSerializer, ADPostSerializer, AdSerializer
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from ..models import Order
from ADS.models import ADS
from ..models import Assigned_Benefits
from PremiumPlan.models import UserPremiumPlan, PremiumPlan
from PremiumPlan.serializers import PremiumPlanSerializer
from rest_framework import permissions
from ..constants import PaymentStatus
from razorpay.errors import SignatureVerificationError



rz_client = RazorpayClient()


class ADPremiumPlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        Adplan = PremiumPlan.objects.filter(type='Ads')
        serializer = PremiumPlanSerializer(Adplan, many=True)
        return Response({'data': serializer.data, 'msg': 'Plans to Post Ad'}, status=status.HTTP_200_OK)
    


class ADSPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request):
        serializer = ADPaymentSerializer(data=request.data)

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


class ADPaymentCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = ADPaymentCompleteSerializer(request.data)

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

        Assigned_Benefits.objects.create(user=order.user, ads_allowed=500)
        userplan = UserPremiumPlan.objects.get(user=order.user)
        userplan.is_active = True
        

        response = {
            "status_code": status.HTTP_201_CREATED,
            "message": "Transaction created"
        }

        return Response(response, status=status.HTTP_201_CREATED)
    

#Remain some work to complete if user.has_business():
class AdsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = ADPostSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            try:
                benefits = Assigned_Benefits.objects.filter(user=user)
            except:
                return Response({'msg': 'User has no Assigned Benefits'})
            
            # for assigned_benefits in benefits:
            #     if assigned_benefits.ads_allowed > benefits.ads_posted:
            #         if user.has_business:
            #             serializer.save(posted_by=user)
            #             return Response({'msg': 'Ad posted Successfully'})
            #         else:
            #             return Response({'msg': 'You do not have an existing business. Please create one'})

            #     elif benefits.ads_allowed == benefits.ads_posted:
            #         benefits.ads_allowed = 0
            #         return Response({'msg': 'Your plan has Expired'})
            #     else:
            #         pass
                
            #     benefits.ads_posted += 1
            #     benefits.save()

            #     return Response({'msg': 'Ads Posted Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


    def get(self, request):
        ads = ADS.objects.all()
        serializer = AdSerializer(ads, many=True)
        return Response({'data': serializer.data})
    
    
