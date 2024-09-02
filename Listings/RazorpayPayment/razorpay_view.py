from rest_framework.views import APIView
from rest_framework import status
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from rest_framework.response import Response
from .razorpay_serializer import RazorpayorderSerializer, RazorPayOrderCompletionSerializer
from rest_framework import permissions
from razorpay.errors import SignatureVerificationError


rz_client = RazorpayClient()



class RazorpayOrderAPIView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        razorpay_serializer = RazorpayorderSerializer(data=request.data)

        if razorpay_serializer.is_valid():
            amount = razorpay_serializer.validated_data.get('amount')
            order_response = rz_client.create_order(
                                   amount=amount
                                   )
            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Order Created',
                'data': order_response
            }

            provider_order_id = order_response.get("id")
           
            # Order2.objects.create(amount=amount, provider_order_id=provider_order_id)
            return Response(response, status=status.HTTP_201_CREATED)
        
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": razorpay_serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        



class CompletePaymentAPIView(APIView):
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        order_serializer = RazorPayOrderCompletionSerializer(data=request.data)

        order_serializer.is_valid(raise_exception=True)

        order_id = order_serializer.validated_data.get('provider_order_id')
        payment_id = order_serializer.validated_data.get('payment_id')
        signature_id = order_serializer.validated_data.get('signature_id')

        try:
                rz_client.verify_payment_signature(
                    razorpay_order_id=order_id,
                    razorpay_payment_id=payment_id,
                    razorpay_signature=signature_id
                )
        except SignatureVerificationError as e:
           
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Payment signature verification failed",
                "error": str(e) 
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

            
        
        # try:
        #     order = Order2.objects.get(provider_order_id=order_id)

        # except Order2.DoesNotExist:
        #     response_data = {
        #         "status_code": status.HTTP_400_BAD_REQUEST,
        #         "message": "Order with the specified provider_order_id not found",
        #     }
        #     return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # order.payment_id = payment_id
        # order.signature_id = signature_id
        # order.isPaid = True
        # order.status = PaymentStatus.SUCCESS
        # order.save()

        # Assigned_Benefits.objects.create(ads_allowed=500)

        response = {
            "status_code": status.HTTP_201_CREATED,
            "message": "transaction created"
        }
        
        return Response(response, status=status.HTTP_201_CREATED)
        
        