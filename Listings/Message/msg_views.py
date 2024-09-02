from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .msg_serializers import MessagePaymentSerializer, MessagePaymentCompleteSerializer, MessageSendSerializer
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from ..models import Order,TextMessage, Category
from ADS.models import ADS
from ..models import Assigned_Benefits
from PremiumPlan.models import UserPremiumPlan, PremiumPlan
from PremiumPlan.serializers import PremiumPlanSerializer
from rest_framework import permissions
from ..constants import PaymentStatus
from razorpay.errors import SignatureVerificationError
from .tasks import send_message
from users.models import User



rz_client = RazorpayClient()


class MessagePremiumPlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        Adplan = PremiumPlan.objects.filter(type='Ads')
        serializer = PremiumPlanSerializer(Adplan, many=True)
        return Response({'data': serializer.data, 'msg': 'Plans to Post Ad'}, status=status.HTTP_200_OK)
    


class MessagePaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request):
        serializer = MessagePaymentSerializer(data=request.data)

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
    


class MessagePaymentCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = MessagePaymentCompleteSerializer(request.data)

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
   
    
#Remaining Task
#Use the for loop using celery
#Have some issue check
class MessageSendAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = MessageSendSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)

        message_body    = serializer.validated_data.get('message')
        category_id     = serializer.validated_data.get('category')
        user            = request.user
       
        cat = get_object_or_404(Category, id=category_id)
        business_users = User.objects.filter(business__category=cat)

        if business_users.exists():
            receivers = business_users        
            benefits = Assigned_Benefits.objects.filter(user=user) 

            #Have some issue check
            for receiver in receivers:      
                if benefits.message_allowed > benefits.messages_used:
                    message = TextMessage(sender=user,category=cat, message=message_body)
                    message.save()
                    message.receiver.set([receiver])
                    
                elif benefits.message_allowed == benefits.messages_used:
                    benefits.message_allowed = 0
                    benefits.save()
                    return Response({'msg': 'Plan has Expired'})
                else:
                    return Response({'msg': 'Plan has Expired22'}, status=status.HTTP_200_OK)
            
                benefits.messages_used += 1
                benefits.save()
                
                url = f'http://localhost:8000/api/user-business-page/{receiver.id}/'
                # send_message(receiver.mobile_number, url, message_body)

            return Response({'msg': 'Message Sent Successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No Business found in this ID'})


    def get(self, request):
        messages = TextMessage.objects.all()
        serializer = MessageSendSerializer(messages, many=True)
        return Response({'msg': 'Data Fetched Successfully', 'data': serializer.data})

