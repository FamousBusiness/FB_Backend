from django.utils import timezone
from django.views import View
import pandas as pd
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
#Payment Imports
import json
import base64
import requests
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from cryptography.hazmat.primitives import hashes
from django.views.decorators.csrf import csrf_exempt
from cryptography.hazmat.backends import default_backend
from django.utils import timezone
from PremiumPlan.models import PremiumPlanOrder
from decouple import config









class SendTESTSMSView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        url = "http://trans.smsfresh.co/api/sendmsg.php"

        message_text = 'You%20have%20a%20new%20lead%20on%20FamousBusiness.in!%20Please%20contact%20the%20customer%20to%20follow%20up.%20Regards%2C%20WFBSPL%20%2008062181258'


        params = {
            "user": 'WEBZOTICAPROMO',
            "pass": '123456',
            "sender": 'WBFSPL',
            "phone": '8249258412',
            # "text": 'New%20Lead%20Alert%20from%20Famous%20Business.%20Please%20view%20the%20Leads%20and%20contact%20to%20the%20Buyer%3A%20https%3A%2F%2Ffamousbusiness.in%2Fleads.%20Regards%2C%20WFBSPL.',
            "text": message_text,
            "priority": 'ndnd',
            "stype": 'normal'
        }
        
        response = requests.get(url, params=params)
        # print('response', response)

        if response.status_code == 200:
            return Response({"message": "API request successful", "response": response.text}, status=status.HTTP_200_OK)
        else:
            return Response({"message": f"API request failed with status code {response.status_code}", "response": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      



def calculate_sha256_string(input_string):
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    sha256.update(input_string.encode('utf-8'))
    return sha256.finalize().hex()



def base64_encode(input_dict):
    json_data = json.dumps(input_dict)
    data_bytes = json_data.encode('utf-8')
    return base64.b64encode(data_bytes).decode('utf-8')



def index(request):
    return render(request, "index.html", { 'output': "Please Pay & Repond From The Payment Gateway Will Come In This Section", 'main_request': "" })




def pay(request):
    transaction_id = str(uuid.uuid4())
    
    MAINPAYLOAD = {
        "merchantId": "M22BWNC10OPNQ",
        "merchantTransactionId": transaction_id,
        "merchantUserId": "FBM225",
        "amount": 100,
        # "redirectUrl": "http://127.0.0.1:8000/message-api/payment-successfull/",
        "redirectUrl": f"http://127.0.0.1:8000/message-api/return-to-me/?lead_id={5}/",
        "redirectMode": "POST",
        # "callbackUrl": "http://127.0.0.1:8000/message-api/payment-successfull/",
        "callbackUrl": f"http://127.0.0.1:8000/message-api/return-to-me/?lead_id={5}/",
        "mobileNumber": "9883835373",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    INDEX = "1"
    ENDPOINT = "/pg/v1/pay"
    SALTKEY = config('SALT_KEY')
    base64String = base64_encode(MAINPAYLOAD)
    mainString = base64String + ENDPOINT + SALTKEY
    sha256Val = calculate_sha256_string(mainString)
    checkSum = sha256Val + '###' + INDEX

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': checkSum,
        'accept': 'application/json',
    }

    json_data = {
        'request': base64String,
    }

    response = requests.post('https://api.phonepe.com/apis/hermes/pg/v1/pay', headers=headers, json=json_data)

    response.raise_for_status()
    responseData = response.json()
    return redirect(responseData['data']['instrumentResponse']['redirectInfo']['url'])





@csrf_exempt
def Payment_Successfull(request):
    form_data = request.POST
    print(form_data)
    return HttpResponse("Success")



# @csrf_exempt
# def payment_return(request):
#     INDEX = "1"
#     SALTKEY = ""
#     form_data = request.POST
#     print(form_data)
#     print(form_data.get('code'))
#     form_data_dict = dict(form_data)

#     print('Hii')
#     transaction_id = form_data.get('transactionId', None)

#     if transaction_id:
#         request_url = 'https://api.phonepe.com/apis/hermes/status/FBM225/' + transaction_id
#         sha256_Pay_load_String = '/pg/v1/status/FBM225/' + transaction_id + SALTKEY
#         sha256_val = calculate_sha256_string(sha256_Pay_load_String)
#         checksum = sha256_val + '###' + INDEX

#         headers = {
#             'Content-Type': 'application/json',
#             'X-VERIFY': checksum,
#             'X-MERCHANT-ID': transaction_id,
#         }

#         response = requests.get(request_url, headers=headers)
#     else:
#         lead = Lead.objects.create(created_by='Naresh')

#     return HttpResponse()

    # return render(request, 'index.html', {'output': response.text, 'main_request': form_data_dict})






# @api_view(['POST'])
# @permission_classes([AllowAny])
@csrf_exempt
def payment_return(request):
    INDEX = "1"
    SALTKEY = config('SALT_KEY')
   
    form_data = request.POST
    lead_id = request.GET.get("lead_id")
    status  = form_data.get('code')
    # print(status)
    form_data_dict = dict(form_data)

    # print(form_data)
    # print(f"POST Data:{form_data}")
    # print(f"Lead: {lead_id}")

    transaction_id = form_data.get('transactionId', None)
    merchant_id    = form_data.get("merchantId", None)
    lead_id        = request.GET.get('lead_id')
        

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

        if status == "PAYMENT_SUCCESS":
            return redirect('https://www.famousbusiness.in/success') 
        else:
            return redirect("https://www.famousbusiness.in/failure")

    return redirect("https://www.famousbusiness.in/leads")
    # return render(request, 'index.html', {'output': response.text, 'main_request': form_data_dict})



# class LeadCheck(generics.ListAPIView):
#     permission_classes = [permissions.AllowAny]
#     # pagination_class   = PageNumberPagination

#     def post(self, request):
#         current_date = timezone.now().date()
#         current_month = current_date.month
#         current_year  = current_date.year

#         leads = Lead.objects.filter(
#         created_at__date=current_date, 
#         created_at__month=current_month,
#         created_at__year=current_year,
#         mail_sent=False)

#         for lead in leads:
#             business_pages = Business.objects.filter(category=lead.category, city=lead.city)
            
#             for business in business_pages:
#                 print(business)
                
#             break
        
#         return Response({'msg': 'Success'})
    

class LeadCheck(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        current_date = timezone.now()
        # days_since_purchase = (current_date - order.purchased_at).days

        return Response("Done")
    



# @method_decorator
class SendWhatsAppTestMessage(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        api_url = "https://bhashsms.com/api/sendmsg.php"
        # api_url = "http://trans.smsfresh.co/api/sendmsg.php"
        business_name = "Ranjit"
        category = "Interior"
        Email    = "ranjit@mail.com"

        params = {
            "user" : "WEBZOTICA",
            "pass" : "123456",
            "sender" : "BUZWAP",
            "phone" : "8920780083",
            "text": "final_001", # Name, Lead id, Category leads_final1
            "priority" : "wa",
            "stype" : "normal",
            "Params": f"{business_name}, {category}, {Email}",
            "htype" : "image",
            "imageUrl" : "https://mdwebzotica.famousbusiness.in/LeadBannerImage/lead_banner_img.jpg"
        }

        url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"
 
        response = requests.get(url, params=params)

        print('response', response)
        # print(response)
        if response.status_code == 200:
            return Response("Message sent Successfully")
        else:
            return Response("Unable to send Whatsapp Message")
        



##### Send Document In Whatsapp Message
class SendDocumentWhatsAppMessage(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        api_url = "https://bhashsms.com/api/sendmsg.php"

        params = {
            "user" : "WEBZOTICA",
            "pass" : "123456",
            "sender" : "BUZWAP",
            "phone" : "8249258412",
            "text": "plan_invoice", 
            "priority" : "wa",
            "stype" : "normal",
            # "Params": "1",
            "htype" : "document",
            "imageUrl" : "https://mdwebzotica.famousbusiness.in/InvoiceDocument/test1.pdf"
        }

        url = f"{api_url}?user={params['user']}&pass={params['pass']}&sender={params['sender']}&phone={params['phone']}&text={params['text']}&priority={params['priority']}&stype={params['stype']}&htype={params['htype']}&url={params['imageUrl']}"

        response = requests.get(url, params=params)

        print('response', response)
        # print(response)
        if response.status_code == 200:
            return Response("Message sent Successfully")
        
        else:
            return Response("Unable to send Whatsapp Message")
        





class PremiumPlanOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PremiumPlanOrder
        fields = ['invoice']


from datetime import date
### Premiumplan Order invoice url check
class PremiumPlanOrderInvoices(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        all_orders = PremiumPlanOrder.objects.all()
            
        serializer = PremiumPlanOrderSerializer(all_orders, many=True)

        return Response(serializer.data)
        




        

