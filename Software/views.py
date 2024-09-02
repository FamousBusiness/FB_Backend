from django.shortcuts import redirect
from django.views import View
from rest_framework.views import APIView
from rest_framework import permissions, status
from .serializer import SoftwarePaymentSerializer, SoftwarePaymentCompleteSerializer
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from .models import SoftwareOrder
from rest_framework.response import Response
from Listings.constants import PaymentStatus
from razorpay.errors import SignatureVerificationError
from Software.phonepepayment import SoftwarePaymentInitiation
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from decouple import config
import requests
from Phonepe.payment import calculate_sha256_string



CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
rz_client = RazorpayClient()




#Payment initiation To Purchase a Lead
class SoftwarePaymentInitiationAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = SoftwarePaymentSerializer(data=request.data)

        if serializer.is_valid():
            received_amount = serializer.validated_data.get('amount')
            amount          = received_amount * 100
            current_user    = request.user
            name            = request.data.get('name')

            try:
                order          = SoftwareOrder.objects.create(user=current_user, amount=received_amount)
                transaction_id = order.transaction_id

                payment_response = SoftwarePaymentInitiation(transaction_id, amount, name)
                return Response({'msg': 'Payment initiation successful', 'payment_response': payment_response},
                                status=status.HTTP_200_OK)
            
            except SoftwareOrder.DoesNotExist:
                return Response({'msg': 'Unable to Create the Order'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)  
        


#Payment Complete after purchasing a Lead
@method_decorator(csrf_exempt, name='dispatch')
class SoftwarePaymentCompletView(View):
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        INDEX        = "1"
        SALTKEY      = config("SALT_KEY")

        #Phonepe Response
        payment_status = request.POST.get('code', None)
        merchant_id = request.POST.get('merchantId', None)
        transaction_id = request.POST.get('transactionId', None)
        check_sum = request.POST.get('checksum', None)
        provider_reference_id = request.POST.get('providerReferenceId', None)
        merchant_order_id = request.POST.get('merchantOrderId', None)

        #Query Params
        name         = request.GET.get('name')

        if transaction_id:
            request_url = 'https://api.phonepe.com/apis/hermes/status/FBM225/' + transaction_id
            sha256_Pay_load_String = '/pg/v1/status/FBM225/' + transaction_id + SALTKEY
            sha256_val = calculate_sha256_string(sha256_Pay_load_String)
            checksum = sha256_val + '###' + INDEX

            headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum,
            'X-MERCHANT-ID': transaction_id,
            }

            response = requests.get(request_url, headers=headers)

            try:
                order = SoftwareOrder.objects.get(transaction_id=transaction_id)
            except SoftwareOrder.DoesNotExist:
                response_data = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Client Order with the specified provider_order_id not found",
                    }
                return redirect("https://www.famousbusiness.in/")

            order.provider_reference_id = provider_reference_id
            order.merchant_id           = merchant_id
            order.checksum              = check_sum
            order.status                = payment_status
            order.isPaid                = True
            order.details               = f'Purchased {name} Software'
            order.message               = response.text
            order.merchant_order_id     = merchant_order_id
            user                        = order.user
            order.save()

            return redirect("https://www.famousbusiness.in/success")
        else:
            return redirect("https://www.famousbusiness.in/failure")

    