from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from .serializers import ADPaymentSerializer, AdPaymentCompleteSerializer, AllADPlanSerializer
from Listings.models import Business, Category
from Listings.constants import PaymentStatus
from razorpay.errors import SignatureVerificationError
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from ADS.models import ADPLANS, Orders, ADS, AD_STATUS, ADImage, AdBucket
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator



rz_client = RazorpayClient()



class AllADPlansAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        all_add_plans = ADPLANS.objects.all()
        serializer    = AllADPlanSerializer(all_add_plans, many=True)

        return Response({'msg': "Data Fetched Successfully", 'data': serializer.data})




#Payment initiation To Purchase a Lead

class ADPaymentInitiateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    @method_decorator(csrf_protect, name='dispatch')
    def post(self, request):
        serializer = ADPaymentSerializer(data=request.data)

        if serializer.is_valid():
            amount         = serializer.validated_data.get('amount')
            current_user   = request.user

            razorpay_order = rz_client.create_order(
                amount=amount
            )

            provider_order_id = razorpay_order.get("id")

            response = {
                'status': status.HTTP_201_CREATED,
                'message': 'Order Created',
                'data': razorpay_order,
            }  

            order = Orders.objects.create(provider_order_id=provider_order_id, amount=amount,
                                  user=current_user)
            order.save()

        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)  

        return Response({'msg': 'Order Created Successfully', 'order_data': response}, status=status.HTTP_200_OK) 
        


#Payment Complete after purchasing a Lead
class ADPaymentCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = AdPaymentCompleteSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        order_id     = serializer.validated_data.get('provider_order_id')
        payment_id   = serializer.validated_data.get('payment_id')
        signature_id = serializer.validated_data.get('signature_id')
        current_user = request.user
        ad_title     = request.data.get('title')
        ad_category  = request.data.get('ad_category')
        ad_city      = request.data.get('city')
        ad_condition = request.data.get('condition')
        images_data  = request.data.getlist('images')
        ad_plan      = request.data.get('plan')

        try:
            order = Orders.objects.get(provider_order_id=order_id)
        except Orders.DoesNotExist:
            return Response({'msg': 'Order Does Not Exist'})
        
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
            order.status = PaymentStatus.CANCEL
            order.isPaid = True
            order.save()
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        category_id = Category.objects.get(type=ad_category)

        for image_data in images_data:
            ADImage.objects.create(ad=ads, image=image_data)

        #Default status of AD is Pending
        ads = ADS.objects.create(
            posted_by = current_user,
            title     = ad_title,
            category  = category_id,
            city      = ad_city,
            condition = ad_condition,
        )

        try:
            plans = ADPLANS.objects.get(name__icontains = ad_plan)
        except ADPLANS.DoesNotExist:
            plans = None

        AdBucket.objects.create(
            posted_by = current_user,
            ad_plan   = plans.pk,
            views     = plans.views_quantity,
            is_paid   = True,
            ad        = ads.pk
        )

        order.payment_id   = payment_id
        order.signature_id = signature_id
        order.isPaid       = True
        order.status       = PaymentStatus.SUCCESS
        order.details      = f'Purchased AD ID: {ads.ad_id}'
        order.ad_plan      = ad_plan
        order.ad           = ads
        order.save()
        
        return Response({'msg': f'Dear {current_user} your Ad created successful'}, status=status.HTTP_200_OK)
    

