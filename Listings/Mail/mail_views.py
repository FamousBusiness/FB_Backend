from django.shortcuts import get_object_or_404, render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .mail_serializers import MailPaymentSerializer, MailPaymentCompleteSerializer
from Listings.RazorpayPayment.razorpay.main import RazorpayClient
from ..models import Order, TextMessage, Category, Business
from ADS.models import ADS
from ..models import Assigned_Benefits
from PremiumPlan.models import UserPremiumPlan, PremiumPlan
from PremiumPlan.serializers import PremiumPlanSerializer
from rest_framework import permissions
from ..constants import PaymentStatus
from razorpay.errors import SignatureVerificationError
# from .tasks import send_message
from users.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags


rz_client = RazorpayClient()


class MailPremiumPlanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        Adplan = PremiumPlan.objects.filter(type='Ads')
        serializer = PremiumPlanSerializer(Adplan, many=True)
        return Response({'data': serializer.data, 'msg': 'Plans to Post Ad'}, status=status.HTTP_200_OK)
    


class MailPaymentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request):
        serializer = MailPaymentSerializer(data=request.data)

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
    


class MailPaymentCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        serializer = MailPaymentCompleteSerializer(request.data)

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
    


# , 'arshadiqbal9871@gmail.com'
# def send_email(request):
#    business_id = Business.objects.get(id=1)
#    subject = "Elevate Your Business with Exclusive PAN India Leads"
#    message = "<h1>Hii Thankyou for subscribing</h1>"
#    email_from = 'customercare@famousbusiness.in'
#    recipient_list = ['sahooranjitkumar53@gmail.com']
#    html_content = render_to_string('../templates/mail/send_mail.html', {'business_id': business_id})
# #    css_content = render_to_string('../static/mail_css/send_mail.css')
#    html_message = f'''
#                     {html_content}
#                      '''

#    send_mail(subject,message, email_from, recipient_list, html_message=html_message )   

#    return HttpResponse("Mail Sent Succefully")



def send_email(request):
    html_message = render_to_string("../templates/mail/send_mail.html")
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject = 'Elevate Your Business with Exclusive PAN India Leads', 
        body = plain_message,
        from_email = 'customercare@famousbusiness.in' ,
        to= ['sahooranjitkumar53@gmail.com']
            )

    message.attach_alternative(html_message, "text/html")
    message.send()
    return HttpResponse("Mail Sent Succefully")

def send_mail_template_testing(request):
    business_id = Business.objects.get(id=1)
    return render(request, 'mail/send_mail.html', {'business': business_id})
